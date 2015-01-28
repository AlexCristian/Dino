import pygame
import os

BOX_COLOR = {}
BOX_COLOR_SHADOW = {}
WEATHER_IMAGE = {}
BOX_COLOR["OK"] = pygame.Color(62, 102, 23)
BOX_COLOR_SHADOW["OK"] = pygame.Color(55, 91, 20)
BOX_COLOR["ERROR"] = pygame.Color(202, 7, 0)
BOX_COLOR_SHADOW["ERROR"] = pygame.Color(180, 6, 0)
BOX_COLOR["WARNING"] = pygame.Color(250, 105, 0)
BOX_COLOR_SHADOW["WARNING"] = pygame.Color(223, 93, 0)

class Project:
    def __init__(self, name, status, health_score):
        self.name = name
        self.status = status
        self.color = BOX_COLOR[self.status]
        self.color_shadow = BOX_COLOR_SHADOW[self.status]
        self.health = health_score
        self.culprits = []
        self.comment = ""
        self.buildtime = None
    def set_buildtime(self, timestamp):
        self.buildtime = timestamp
    def add_culprit(self, name):
        self.culprits.append(name)
    def add_build_comment(self, comment):
        self.comment = (comment[:30] + '...') if len(comment) > 30 else comment

