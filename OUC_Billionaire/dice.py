# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 10:28:09 2019

@author: Sherlock Holmes
"""

import pygame
import random

class Dice():
    """骰子类"""
    def __init__(self, screen, messageboard):
        self.screen = screen
        self.messageboard = messageboard
        # 存储骰子每个面的图像
        self.dice_side = []
        #显示骰子
        self.show_dice = True
        # 导入骰子的图片
        for i in range(1, 7):
            file_name_str = "dice" + str(i)
            file_path_str = "images/" + file_name_str + ".png"
            dice_image = pygame.image.load(file_path_str)
            self.dice_side.append(dice_image)
        # 设置当前骰子的面图片以及位置参数
        self.cur_dice = self.dice_side[0]
        self.rect = self.cur_dice.get_rect()
        self.rect.center = self.messageboard.box_1.center

        # 秘密控制相关属性
        self._secret_control = False  # 秘密控制模式
        self._forced_value = None     # 强制设定的骰子值
        self._control_keys = {
            pygame.K_F1: 1,
            pygame.K_F2: 2,
            pygame.K_F3: 3,
            pygame.K_F4: 4,
            pygame.K_F5: 5,
            pygame.K_F6: 6
        }
    
    def _handle_secret_control(self, event):
        """处理秘密控制按键"""
        if event.type == pygame.KEYDOWN:
            if pygame.K_F1 <= event.key <= pygame.K_F6:
                self._forced_value = event.key - pygame.K_F1 + 1
                print(f"[DEBUG] 骰子点数强制设为: {self._forced_value}")
                return True
            elif event.key == pygame.K_F12:
                self._forced_value = None
                print("[DEBUG] 骰子恢复随机模式")
                return True
        return False

    def draw_dice(self, dice_image):
        """绘制骰子"""
        self.screen.blit(dice_image, self.rect)
    
    def roll_dice(self):
        """掷骰子"""
        #print("rolling dice...")
        # 随机骰子的值并制造出骰子随机的效果

        if self._forced_value is not None:
            # 秘密控制模式下直接返回预设值
            value = self._forced_value
            self.cur_dice = self.dice_side[value - 1]
            self.draw_dice(self.cur_dice)
            pygame.display.update()
            return value
        
        final_index=0
        
        for i in range(1, 18):
            index = random.randint(0, 5)
            self.cur_dice = self.dice_side[index]
            self.draw_dice(self.cur_dice)
            pygame.display.update()
            pygame.time.wait(100)
            final_index = index
        # 骰子最后停下时的值
        # result = random.randint(0, 5)
        self.cur_dice = self.dice_side[final_index]
        # self.cur_dice=self.dice_side[2]
        self.draw_dice(self.cur_dice)
        return final_index + 1
        # return 2
        