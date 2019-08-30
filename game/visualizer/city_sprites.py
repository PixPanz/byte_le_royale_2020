import pygame
from game.common.enums import CityLevel
from game.visualizer.sprite_sheet_functions import *

class CitySprite(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet_data, x,y, city_level):
        super().__init__()
        sprite_sheet = SpriteSheet("game/visualizer/assets/city_assets/city_default.png")
        self.image = sprite_sheet.get_image(sprite_sheet_data[0], sprite_sheet_data[1], sprite_sheet_data[2], sprite_sheet_data[3])

class CitySpriteLevel0(CitySprite):
    def __init__(self, x, y, city_level):
        CitySprite.__init__(self, [0, 0, 300, 300], x, y, city_level)
class CitySpriteLevel1(CitySprite):
    def __init__(self, x, y, city_level):
        CitySprite.__init__(self, [0, 0, 1000, 1000], x, y, city_level)
class CitySpriteLevel2(CitySprite):
    def __init__(self, x, y, city_level):
        CitySprite.__init__(self, [0, 0, 1000, 1000], x, y, city_level)
class CitySpriteDestroyedLevel0(CitySprite):
    def __init__(self, x, y, city_level):
        CitySprite.__init__(self, [0, 0, 1000, 1000], x, y, city_level)
class CitySpriteDestroyedLevel1(CitySprite):
    def __init__(self, x, y, city_level):
        CitySprite.__init__(self, [0, 0, 1000, 1000], x, y, city_level)
class CitySpriteDestroyedLevel2(CitySprite):
    def __init__(self, x, y, city_level):
        CitySprite.__init__(self, [0, 0, 1000, 1000], x, y, city_level)





