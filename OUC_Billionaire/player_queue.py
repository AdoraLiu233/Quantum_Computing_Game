# -*- coding: utf-8 -*-
class PlayerQueue():
    """玩家队列类，用于管理玩家的轮流游戏"""
    def __init__(self):
        # 列表模拟玩家队列
        self.queue = []
        # 队列的长度
        self.size = 0
        # 当前轮到哪个玩家游戏
        self.cur_player = None
        # 当前游戏回合玩家的下标
        self.cur_player_index = -1
        self.round_completed = False
    
    def empty(self):
        """判断队列是否为空"""
        if self.size == 0:
            return True
        else:
            return False
    
    def add_player(self, player):
        """向队列中添加玩家"""
        self.queue.append(player)
        self.size += 1
        # 同时更新当前游戏玩家和当前游戏玩家下标
        self.cur_player_index = 0
        self.cur_player = self.queue[self.cur_player_index]
    
    def next_round(self):
        """实现游戏中玩家回合的更替"""
        # 获得下一轮游戏的玩家的下标
        self.cur_player_index = (self.cur_player_index + 1) % self.size
        self.cur_player = self.queue[self.cur_player_index]
        if self.cur_player_index == 0:
            self.round_completed = True
        else:
            self.round_completed = False

    def is_round_completed(self):
        """检查当前轮次是否完成"""
        return self.round_completed
    
    def reverse_draw(self):
        """逆序绘制队列中的玩家（图片位置）"""
        for index in range(self.size - 1, -1, -1):
            # print(f"Player {self.queue[index].player_name}'s pos: ", self.queue[index].pos)
            self.queue[index].draw_player()
