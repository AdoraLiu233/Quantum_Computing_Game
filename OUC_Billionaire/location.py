# -*- coding: utf-8 -*-
import pygame
import random
import math
from player import Qubit
import tools as tool

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
        self.isShop = False
        self.can_give_qubit = False  # 是否可以给予Qubit
        self.can_give_item = False   # 是否可以给予道具
        self.item_pool = []          # 道具池
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
        
    def get_random_qubit(self):
        """生成随机Qubit"""
        # 随机生成α和β，保证归一化
        angle = random.uniform(0, 2 * math.pi)
        alpha = math.cos(angle)
        beta = math.sin(angle)
        return Qubit(alpha, beta)
    
    def get_random_item(self):
        """从道具池随机获取道具"""
        return random.choice(self.item_pool) if self.item_pool else None

    # 问题：需要在每个地点显示说明文字吗   
    # def draw_location(self):
    #     """在屏幕上绘制地点圆点并且显示说明文字"""
    #     pygame.draw.circle(self.screen, self.color, (self.x, self.y), 
    #                        self.radius, 0)
    #     self.screen.blit(self.name_image, self.name_rect)
        
        
class Dorm(Location):
    """宿舍（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None):
        # 继承父类的构造方法
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id)
    
    def trigger_event(self, player = None):
        """触发事件"""
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        elif self.isShop:
            return "TRIGGER_SHOP"
        # 随机事件的编号
        index = 0
        return index
    
    
class ScienceBuilding(Location):
    """理科楼（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None):
        # 继承父类的构造方法
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id)

    def trigger_event(self, player):
        """触发事件"""
        # 随机事件的编号
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        elif self.isShop:
            return "TRIGGER_SHOP"
    
class Hall(Location):
    """大礼堂（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None):
        # 继承父类的构造方法
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id)
        self.can_give_qubit = True

    def trigger_event(self, player):
        """触发事件"""
        # 随机事件的编号
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        elif self.isShop:
            return "TRIGGER_SHOP"
        elif self.can_give_qubit:
            return "GET_RANDOM_QUBIT"
        index = 2
        return index

class OfficePlace(Location):
    """工字厅（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None):
        # 继承父类的构造方法
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id)
        self.item_pool=[tool.StealCard()]
        self.can_give_item = True

    def trigger_event(self, player):
        """触发事件"""
        # 随机事件的编号
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        elif self.isShop:
            return "TRIGGER_SHOP"
        elif self.can_give_item:
            return "GET_RANDOM_ITEM"
        index = 9
        return index
    
class Stadium(Location):
    """体育馆（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None):
        # 继承父类的构造方法
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id)

    def trigger_event(self, player):
        """触发事件"""
        # 随机事件的编号
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        elif self.isShop:
            return "TRIGGER_SHOP"
        index = 3
        return index
    
class MainBuilding(Location):
    """主楼（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None):
        # 继承父类的构造方法
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id)

    def trigger_event(self, player):
        """触发事件"""
        # 随机事件的编号
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        elif self.isShop:
            return "TRIGGER_SHOP"
        index = 4
        return index
    
class StudyHall(Location):
    """清华学堂（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None):
        # 继承父类的构造方法
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id)

    def trigger_event(self, player):
        """触发事件"""
        # 随机事件的编号
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        elif self.isShop:
            return "TRIGGER_SHOP"
        index = 5
        return index
    
class Gate(Location):
    """二校门（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None):
        # 继承父类的构造方法
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id)
        self.isShop = True

    def trigger_event(self, player):
        """触发事件"""
        # 随机事件的编号
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        elif self.isShop:
            return "TRIGGER_SHOP"
        index = 6
        return index
    
class TechnologyBuilding(Location):
    """李兆基楼（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None):
        # 继承父类的构造方法
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id)

    def trigger_event(self, player):
        """触发事件"""
        # 随机事件的编号
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        elif self.isShop:
            return "TRIGGER_SHOP"
        index = 7
        return index
    
class ArtMuseum(Location):
    """艺术博物馆（继承地点类）"""
    def __init__(self, ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id=None):
        # 继承父类的构造方法
        super().__init__(ai_settings, screen, index, pos_x, pos_y, msg, mini_game_id)

    def trigger_event(self, player):
        """触发事件"""
        # 随机事件的编号
        if self.mini_game_id:
            return "TRIGGER_MINI_GAME"
        elif self.isShop:
            return "TRIGGER_SHOP"
        index = 8
        return index
