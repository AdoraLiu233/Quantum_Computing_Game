# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 23:43:40 2019

@author: Sherlock Holmes
"""

import pygame
import random

class Location():
    """地点类"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None): # Added mini_game_id
        self.ai_settings = ai_settings
        self.screen = screen
        self.index = index
        self.x = pos_x
        self.y = pos_y
        self.radius = ai_settings.circle_radius
        self.name = msg
        self.mini_game_id = mini_game_id # Store mini-game ID
        self.text_color = (30, 30, 30)
        self.font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 20)
        self.color = self.ai_settings.circle_color
        self.create_location_name()

    def trigger_event(self, player=None):
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        if self.ai_settings.event_cnt > 3:
            index = random.randint(3, self.ai_settings.event_cnt - 1)
        else:
            index = 0
            # print("Warning: Not enough general events to choose from.") # Optional: Keep or remove print
        return index

    def create_location_name(self):
        name_str = self.name
        self.name_image = self.font.render(name_str, True, self.text_color,
                                            self.ai_settings.bg_color) # Assuming bg_color for transparency
        self.name_rect = self.name_image.get_rect()
        self.name_rect.centerx = self.x
        self.name_rect.top = self.y + self.radius + 10

    def draw_location(self):
        pygame.draw.circle(self.screen, self.color, (self.x, self.y),
                            self.radius, 0)
        self.screen.blit(self.name_image, self.name_rect)


class Hospital(Location):
    """医院类（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None): # Add mini_game_id here
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id) # Pass it to super

    def trigger_event(self, player=None):
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        return 0


class ChemistryInstitute(Location):
    """化院类（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None): # Add mini_game_id here
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id) # Pass it to super

    def trigger_event(self, player):
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        player.pos = random.randint(0, self.ai_settings.location_cnt - 1)
        return 1


class SouthDistrict(Location):
    """南区类（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None): # Add mini_game_id here
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id) # Pass it to super

    def trigger_event(self, player):
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        hospital_pos = 18
        if hasattr(self.ai_settings, 'locations_instance_list'): # Check if the list exists
            for loc in self.ai_settings.locations_instance_list:
                if isinstance(loc, Hospital):
                    hospital_pos = loc.index
                    break
        player.pos = hospital_pos
        return 2