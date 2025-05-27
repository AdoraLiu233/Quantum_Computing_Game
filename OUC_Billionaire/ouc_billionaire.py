# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 23:47:48 2019

@author: Sherlock Holmes
"""

import pygame
from settings import Settings
from button import Button
import game_functions as gf
from dice import Dice
from messageboard import Messageboard
from game_state import GameState
from player_queue import PlayerQueue
import os

def run_game():
    """游戏运行的主函数"""
    # 初始化游戏并创建一个屏幕对象
    pygame.init()
    # 导入设置文件中对窗口的设置
    ai_settings = Settings()
    screen = pygame.display.set_mode(
            (ai_settings.screen_width, ai_settings.screen_height))
    
    # 设置窗口顶部导航栏标题
    pygame.display.set_caption("OUC Billionaire")
    
    # “开始游戏”按钮
    play_button = Button(screen, ai_settings.play_button)
    # 地点编组
    locations = []
    # 地点坐标信息编组
    location_points = []
    # 创建所有地点格子
    gf.create_all_locations(ai_settings, screen, locations, location_points)
    
    # 创建游戏玩家游戏回合顺序队列
    player_que = PlayerQueue()
    gf.create_player_queue(ai_settings, screen, locations, player_que)
    
    # 创建信息板
    messageboard = Messageboard(ai_settings, screen, locations)
    # 创建骰子
    dice = Dice(screen, messageboard)
    
    # 绘制骰子初始状态
    dice.draw_dice(dice.cur_dice)
    
    # 游戏当前的状态
    gs = GameState(ai_settings)
    game_clock = pygame.time.Clock() # 控制游戏帧率
    
    # 游戏的主循环
    while True:
        # 1. 事件处理
        # 如果小游戏正在活动，则主事件循环可能不处理，或者小游戏自己处理
        if gs.game_state == ai_settings.MINI_GAME_ACTIVE:
            # 小游戏接管事件处理和屏幕更新
            gf.run_specific_mini_game(ai_settings, screen, gs, player_que.cur_player)
            # run_specific_mini_game 会在内部处理自己的事件循环和屏幕更新，
            # 并在结束后改变 gs.game_state
        else:
            # 正常游戏流程的事件处理
            gf.check_events(ai_settings, gs, play_button, locations, messageboard, dice, player_que)

        # 2. 屏幕更新 (只有在非小游戏活动状态下，主游戏才更新屏幕)
        if gs.game_state != ai_settings.MINI_GAME_ACTIVE:
            gf.update_screen(ai_settings, screen, gs, play_button, locations,
                             location_points,
                             messageboard, dice, player_que)

        game_clock.tick(30) # 例如，每秒30帧

run_game()
