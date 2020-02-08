import os
import sys
import importlib
import json
import traceback

from tqdm import tqdm

# Load these imports in so the clients can properly load them in later
# Even though these are unused imports, leave them imported so they are able to properly resolve all dependent imports,
# before clients get a chance to import the modules that these are calling, too.
import game.client.user_client
import game.common.enums

from game.common.player import *
from game.config import *
from game.controllers.master_controller import MasterController
from game.utils.helpers import write
from game.utils.secure_importer import secure_importer
from game.utils.thread import Thread, client_thread

clients = list()
current_world = None
master_controller = MasterController()
turn_number = 1


def main():
    loop()


def loop(quiet=False):
    global clients
    global master_controller
    
    f = sys.stdout
    if quiet:
        f = open(os.devnull, 'w')
        sys.stdout = f

    boot()
    world = load()

    for turn in tqdm(master_controller.game_loop_logic(), bar_format=TQDM_BAR_FORMAT, unit=TQDM_UNITS, file=f):
        pre_tick(turn, world)
        tick(turn)
        post_tick(turn)

    print("Game reached max turns and is closing.")

    shutdown()


# Gets players established with their objects and such
def boot():
    global clients
    global master_controller

    current_dir = os.getcwd()
    sys.path.insert(0, current_dir)
    sys.path.insert(0, f'{current_dir}/{CLIENT_DIRECTORY}')

    # Load clients in
    for filename in os.listdir(CLIENT_DIRECTORY):
        filename = filename.replace('.py', '')

        if CLIENT_KEYWORD.upper() not in filename.upper():
            # Filters out files that do not contain CLIENT_KEYWORD in their filename
            continue

        if os.path.isdir(os.path.join(CLIENT_DIRECTORY, filename)):
            # Skips folders
            continue

        player = Player()
        clients.append(player)

        try:
            # Apply import restrictions
            __original_importer = __builtins__['__import__']
            __builtins__['__import__'] = secure_importer
            im = importlib.import_module(f'{filename}', CLIENT_DIRECTORY)
        except ImportError as e:
            print("Client attempted invalid imports.")
            print(e)
            continue
        except Exception:
            message = f'Client {filename} is having problems.'
            player.functional = False
            player.error = traceback.format_exc()
            print(player.error)
            shutdown(message, source='Client_error')
        finally:
            # Restore original importer for server use
            __builtins__['__import__'] = __original_importer

        obj = None
        try:
            obj = im.Client()
        except Exception:
            message = f'Client {filename} is not functional.'
            player.functional = False
            player.error = traceback.format_exc()
            print(player.error)
            shutdown(message, source='Client_error')

        player.code = obj

    debug(f'Clients found: {len(clients)}')
    # Verify correct number of clients
    if SET_NUMBER_OF_CLIENTS_START is not None and len(clients) != SET_NUMBER_OF_CLIENTS_START:
        raise ValueError("Number of clients is not the set value.\n"
                         "Number of clients: " + str(len(clients)) + "  |  Set number: " + str(
            SET_NUMBER_OF_CLIENTS_START))
    elif MIN_CLIENTS_START is not None and len(clients) < MIN_CLIENTS_START:
        raise ValueError("Number of clients is less than the minimum required.\n"
                         "Number of clients: " + str(len(clients)) + "  |  Minimum: " + str(MIN_CLIENTS_START))
    elif MAX_CLIENTS_START is not None and len(clients) > MAX_CLIENTS_START:
        raise ValueError("Number of clients exceeds the maximum allowed.\n"
                         "Number of clients: " + str(len(clients)) + "  |  Maximum: " + str(MAX_CLIENTS_START))

    # Set up player objects
    if SET_NUMBER_OF_CLIENTS_START == 1:
        master_controller.give_clients_objects(clients[0])
    else:
        master_controller.give_clients_objects(clients)


# Loads all of the results of the generate() functionality into memory
def load():
    if not os.path.exists(LOGS_DIR):
        raise FileNotFoundError('Log directory not found.')

    if not os.path.exists(GAME_MAP_FILE):
        raise FileNotFoundError('Game map not found.')

    # Delete previous logs
    [os.remove(os.path.join(LOGS_DIR, path)) for path in os.listdir(LOGS_DIR) if 'turn' in path]

    world = None
    with open(GAME_MAP_FILE) as json_file:
        world = json.load(json_file)
    return world


# Read from the outlined game map and establish the world given
def pre_tick(turn, world):
    global master_controller
    global current_world
    global turn_number

    current_world = world[str(turn)]

    if SET_NUMBER_OF_CLIENTS_START == 1:
        master_controller.interpret_current_turn_data(clients[0], current_world, turn_number)
    else:
        master_controller.interpret_current_turn_data(clients, current_world, turn_number)


# Send client state of the world and a place to put what they want to do
def tick(turn):
    global clients
    global current_world
    global master_controller
    global turn_number

    # Create list of threads that run the client's code
    threads = list()
    for client in clients:
        if not client.functional:
            continue
        arguments = master_controller.client_turn_arguments(client, current_world, turn_number)
        # Create the thread, args being the things the client will need
        thr = Thread(func=client_thread, args=(client, arguments))
        threads.append(thr)

    # Start all of the threads. This is where the client's code is actually be run.
    [thr.start() for thr in threads]

    # Boot up a timer in the meantime so the main thread can move on if a client is taking too long.
    # Will move on earlier if all of the threads are finished first.
    _ = 0
    while True in [thr.is_alive() for thr in threads] and _ < MAX_OPERATIONS_PER_TURN:
        _ += 1

    # Go through all the threads and see which ones are still running.
    for client, thr in zip(clients, threads):
        if thr.is_alive():
            client.functional = False
            print(f'{client.id} failed to reply in time and has been dropped')
        if thr.error is not None:
            client.functional = False
            client.error = thr.error
            print(thr.error)

    # End if there are no remaining clients
    check_game_continue(len([client for client in clients if client.functional]))

    # Apply bulk of game logic
    if SET_NUMBER_OF_CLIENTS_START == 1:
        master_controller.turn_logic(clients[0], current_world, turn_number)
    else:
        master_controller.turn_logic(clients, current_world, turn_number)


# Create log of the turn and end the game if necessary
def post_tick(turn):
    global clients
    global current_world
    global master_controller
    global turn_number

    # Write turn results to log file
    data = None
    if SET_NUMBER_OF_CLIENTS_START == 1:
        data = master_controller.create_turn_log(clients[0], current_world, turn_number)
    else:
        data = master_controller.create_turn_log(clients, current_world, turn_number)

    with open(os.path.join(LOGS_DIR, f"turn_{turn_number:04d}.json"), 'w+') as f:
        json.dump(data, f)

    # Check if game has ended
    if master_controller.game_over_check():
        shutdown()

    turn_number += 1


# Game is over. Create the results file and end the game.
def shutdown(reason="", source='Unknown_error'):
    global clients
    global current_world
    global master_controller
    global turn_number

    # Retrieve results from master controller
    results_information = None
    if SET_NUMBER_OF_CLIENTS_START == 1:
        results_information = master_controller.return_final_results(clients[0], current_world, turn_number)
    else:
        results_information = master_controller.return_final_results(clients, current_world, turn_number)

    if reason:
        results_information[source] = reason

    # Write results file
    write(results_information, RESULTS_FILE)

    # Exit game
    if reason:
        print(f"\nGame has ended due to {source}.")
        os._exit(1)
    else:
        print(f"\nGame has successfully ended. The city lasted {turn_number} turns.")
        os._exit(0)


def check_game_continue(num_clients):
    error = ""
    if SET_NUMBER_OF_CLIENTS_CONTINUE is not None and num_clients != SET_NUMBER_OF_CLIENTS_CONTINUE:
        error = f"Number of clients ({num_clients}) is not SET number ({SET_NUMBER_OF_CLIENTS_CONTINUE}). Ending game."
    elif MIN_CLIENTS_CONTINUE is not None and num_clients < MIN_CLIENTS_CONTINUE:
        error = f"Number of clients ({num_clients}) is less than MIN number ({MIN_CLIENTS_CONTINUE}). Ending game."
    elif MAX_CLIENTS_CONTINUE is not None and num_clients > MAX_CLIENTS_CONTINUE:
        error = f"Number of clients ({num_clients}) is greater than MAX number ({MAX_CLIENTS_CONTINUE}). Ending game."
    else:
        return True
    shutdown(error)
    return False


# Debug print statement
def debug(*args):
    if Debug.level >= DebugLevel.engine:
        print('Engine: ', end='')
        print(*args)


if __name__ == '__main__':
    main()
