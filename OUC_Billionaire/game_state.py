# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 10:45:31 2019

@author: Sherlock Holmes
"""


class GameState():
    """记录游戏统计信息的类"""
    def __init__(self, ai_settings):
        """初始化统计信息"""
        self.ai_settings = ai_settings
        # 游戏刚启动时处于非活动状态
        self.game_active = False
        # 游戏的当前状态
        self.game_state = self.ai_settings.ROLL_DICE
        # 游戏当前事件在事件列表中的下标
        self.cur_event_index = 0

        self.current_round = 1
        self.max_rounds = ai_settings.max_rounds

        self.current_mini_game_id = None    # 当前激活的小游戏ID (例如 "game1")
        self.mini_game_result_message = ""  # 小游戏结束后的结果信息 (例如 "游戏胜利！获得200金钱！")
        self.mini_game_player_effect = None # 小游戏对玩家产生的具体效果（例如金钱变化量）

        self.shop_result_message = ""        # 商店结果信息 (例如 "购买成功！花费50金钱！")
        self.shop_result_effect = 0       # 商店对玩家产生的具体效果（例如金钱变化量）


    def is_game_over(self):
        """检查游戏是否应该结束"""
        return self.current_round > self.max_rounds
        
    def increment_round(self):
        """增加回合数"""
        self.current_round += 1

        
        