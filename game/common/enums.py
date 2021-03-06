class ActionType:
    none = 0
    repair_structure = 1
    regain_population = 2
    accumulate_wealth = 3
    upgrade_city = 4


class CityLevel:
    level_zero = 0
    level_one = 1
    level_two = 2
    level_three = 3


class CityType:
    none = 0
    healthy = 1
    sturdy = 2
    invested = 3
    pyrophobic = 4
    popular = 5
    modern = 6


class DamageScaling:
    low = 0
    medium = 1
    high = 2
    extreme = 3


class DebugLevel:
    none = 0
    client = 1
    controller = 2
    engine = 3


class DecreeType:
    none = -1
    anti_fire_dogs = 0
    paperweights = 1
    snow_shovels = 2
    rubber_boots = 3
    fishing_hook = 4
    cheese = 5


class DisasterStatus:
    live = 1
    dead = 0


class DisasterType:
    fire = 0
    tornado = 1
    blizzard = 2
    earthquake = 3
    monster = 4
    ufo = 5


class DisasterLevel:
    level_zero = 0
    level_one = 1
    level_two = 2
    level_three = 3
    level_four = 4


class EventType:
    city_upgrade = 0
    sensor_upgrade = 1
    building_upgrade = 2
    disaster_spawned = 3
    disaster_eliminated = 4
    effort_applied = 5


class ObjectType:
    none = 0
    action = 1
    disaster = 2
    sensor = 3
    city = 4
    player = 5
    building = 6


class ReactiveType:
    fire_station = 0
    pow_sham = 1
    monster_hunter = 2  # also considered mech


class SensorLevel:
    level_zero = 0
    level_one = 1
    level_two = 2
    level_three = 3


class SensorType:
    fire = 0
    tornado = 1
    blizzard = 2
    earthquake = 3
    monster = 4
    ufo = 5


class BuildingLevel:
    level_zero = 0
    level_one = 1


class BuildingType:
    police_station = 0
    gelato_shop = 1
    big_canoe = 2
    mint = 3
    billboard = 4
    printer = 5
