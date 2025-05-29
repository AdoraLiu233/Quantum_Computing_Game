# -*- coding: utf-8 -*-

import pygame
import os

class Messageboard():
    """显示游戏相关信息的类"""
    def __init__(self, ai_settings, screen, locations):
        self.screen = screen
        self.ai_settings = ai_settings
        self.locations = locations
        
        # 设置面板字体颜色和大小
        self.text_color_1 = (0, 0, 139)
        self.text_color_2 = (0, 0, 0)
        self.font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 18)
        
        # 设置各个面板块的颜色
        self.box_color_1 = self.ai_settings.board_color_1
        self.box_color_2 = self.ai_settings.board_color_2
        self.box_color_3 = self.ai_settings.board_color_3
        
        # 设置面板块位置并创建
        self.box_1 = pygame.Rect(800, 0, 400, 300)
        self.box_2 = pygame.Rect(800, 300, 400, 300)
        self.box_3 = pygame.Rect(800, 600, 400, 400)
        
        self.start_minigame_button_rect = None # 初始化为 None
        self.button_font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 20) # 用于文本按钮

        # 设置结束回合图片路径
        image_path_str = "images/end_round_button.png"
        self.end_round_button = pygame.image.load(image_path_str)

        # 玩家信息列表
        self.player_rendered_msgs = []
        self.player_msg_rects = []
        # --- 结束新增 ---
        self.button_rect = pygame.Rect(0, 0, 160, 50)
        self.quit_button_rect = None

        # 事件消息列表
        self.event_msg = []
        self.event_msg_rect = []
        
    def update_players_message(self, pq):
        """将玩家信息转换为渲染的图像"""
        self.player_rendered_msgs = []
        self.player_msg_rects = []
        # 顺序遍历玩家队列里的所有玩家
        player_cnt = pq.size
        if player_cnt == 0: return

        for i in range(0, player_cnt):
            player = pq.queue[i]
            player_msg_str_1 = player.player_name + "："
            # 安全地获取地点名称
            location_name = "未知"
            if 0 <= player.pos < len(self.locations):
                location_name = self.locations[player.pos].name
            else:
                print(f"Warning: Player {player.player_name} has invalid position {player.pos}")

            player_msg_str_2 = ("拥有金钱：" + str(player.money) + "拥有积分：" + str(player.score) +  "当前位置：" + location_name)
            msg1_img = self.font.render(player_msg_str_1, True, self.text_color_1)
            msg2_img = self.font.render(player_msg_str_2, True, self.text_color_1)
            self.player_rendered_msgs.append([msg1_img, msg2_img])
        
        if not self.player_rendered_msgs:
            return
        
        # 将所有玩家信息放在第二个信息块上
        rect_1 = self.player_rendered_msgs[0][0].get_rect()
        rect_2 = self.player_rendered_msgs[0][1].get_rect()
        # self.player_msg_rects 应该已经被初始化为空列表
        self.player_msg_rects.append([rect_1, rect_2])
        self.player_msg_rects[0][0].top = self.box_2.top + 10
        self.player_msg_rects[0][0].left = self.box_2.left + 10
        self.player_msg_rects[0][1].top = self.player_msg_rects[0][0].bottom + 5
        self.player_msg_rects[0][1].left = self.box_2.left + 10
        
        for i in range(1, player_cnt):
            rect_1 = self.player_rendered_msgs[i][0].get_rect()
            rect_2 = self.player_rendered_msgs[i][1].get_rect()
            self.player_msg_rects.append([rect_1, rect_2])
            self.player_msg_rects[i][0].top = (
                self.player_msg_rects[i - 1][1].bottom + 5)
            self.player_msg_rects[i][0].left = self.box_2.left + 10
            self.player_msg_rects[i][1].top = (self.player_msg_rects[i][0].bottom + 5)
            self.player_msg_rects[i][1].left = self.box_2.left + 10
    
    def update_event_message(self, gs, player):
        """更新事件信息"""
        self.event_msg = []
        self.event_msg_rect = []
        self.start_minigame_button_rect = None # 重置按钮
        
        if gs.game_state == self.ai_settings.ROLL_DICE:
            # 创建初始化信息相关文字
            event_msg_str_list = [(player.player_name + "的游戏回合!"), ("请" + player.player_name + "掷骰子~")]
            for msg_str in event_msg_str_list:
                msg_img = self.font.render(msg_str, True, self.text_color_2)    
                self.event_msg.append(msg_img)
        elif gs.game_state == self.ai_settings.MINI_GAME_STARTING:
            intro_msg_str = f"你来到了小游戏地点: {gs.current_mini_game_id}!"
            game_name = self.ai_settings.minigame_configs.get(gs.current_mini_game_id, {}).get("name", gs.current_mini_game_id)
            intro_msg_str = f"即将开始小游戏: {game_name}!"
            intro_img = self.font.render(intro_msg_str, True, self.text_color_2)
            self.event_msg.append(intro_img)

            # 创建一个文本按钮 "开始小游戏"
            start_button_text = "点击开始小游戏"
            start_button_img = self.button_font.render(start_button_text, True, (255,255,255), (0,128,0)) #白字绿底
            self.event_msg.append(start_button_img)
            # 其 rect 将在下面统一处理位置时创建并赋值给 self.start_minigame_button_rect
        elif gs.game_state == self.ai_settings.MINI_GAME_ACTIVE:
            # 这个状态下，信息板可以显示 "小游戏进行中..."
            # game_name = self.ai_settings.minigame_configs.get(gs.current_mini_game_id, {}).get("name", gs.current_mini_game_id)
            active_msg_str = f"小游戏: {gs.current_mini_game_id} 进行中..."
            active_img = self.font.render(active_msg_str, True, self.text_color_2)
            self.event_msg.append(active_img)

        elif gs.game_state == self.ai_settings.SHOW_MINI_GAME_RESULT:
            if gs.mini_game_result_message:
                result_color = self.text_color_2
                if "胜利" in gs.mini_game_result_message: result_color = (0, 150, 0) # 绿色
                elif "失败" in gs.mini_game_result_message: result_color = (150, 0, 0) # 红色
                
                result_img = self.font.render(gs.mini_game_result_message, True, result_color)
                self.event_msg.append(result_img)
            else:
                self.event_msg.append(self.font.render("小游戏已结束。", True, self.text_color_2))
            # 在此状态下，也显示“结束回合”按钮，其rect在draw_messageboard中处理或者在这里设置
            # self.button_rect 的位置计算应在此处或 draw 中确保
        elif gs.game_state == self.ai_settings.SHOP_ENTERING:
            intro_msg_str = f"你来到了二校门，校外有清华印象文创店，快来补给吧！"
            intro_msg_str = f"即将进入商店!"
            intro_img = self.font.render(intro_msg_str, True, self.text_color_2)
            self.event_msg.append(intro_img)

            # 创建一个文本按钮 "开始小游戏"
            start_button_text = "点击进入商店"
            start_button_img = self.button_font.render(start_button_text, True, (255,255,255), (0,128,0)) #白字绿底
            self.event_msg.append(start_button_img)
            # 其 rect 将在下面统一处理位置时创建并赋值给 self.start_minigame_button_rect
        elif gs.game_state == self.ai_settings.SHOP_ACTIVE:
            # 这个状态下，信息板可以显示 "小游戏进行中..."
            # game_name = self.ai_settings.minigame_configs.get(gs.current_mini_game_id, {}).get("name", gs.current_mini_game_id)
            active_msg_str = f"购买物品中..."
            active_img = self.font.render(active_msg_str, True, self.text_color_2)
            self.event_msg.append(active_img)

        elif gs.game_state == self.ai_settings.SHOP_RESULT:
            print("4444444444444")
            print(gs.shop_result_message)
            if gs.shop_result_message:
                result_color = self.text_color_2
                # if "胜利" in gs.mini_game_result_message: result_color = (0, 150, 0) # 绿色
                # elif "失败" in gs.mini_game_result_message: result_color = (150, 0, 0) # 红色
                render_message1= gs.shop_result_message+" "+ f" 购买花费: {gs.shop_cost} 金钱"
                render_message2= f"当前资金：{player.money} "
                result_img1= self.font.render(render_message1, True, result_color)
                result_img2 = self.font.render(render_message2, True, result_color)
                self.event_msg.append(result_img1)
                self.event_msg.append(result_img2)
            else:
                self.event_msg.append(self.font.render("小游戏已结束。", True, self.text_color_2))

        elif gs.game_state == self.ai_settings.END_ROUND:
            # 创建结束回合按钮信息
            self.button_rect = self.end_round_button.get_rect()
            self.button_rect.bottom = self.box_3.bottom - 10
            self.button_rect.right = self.box_3.right - 10
            self.event_msg.append(self.font.render("事件处理完毕。", True, self.text_color_2))

        # --- 统一处理消息和按钮的位置 ---
        current_y = self.box_3.top + 10
        for i, msg_img in enumerate(self.event_msg):
            msg_rect = msg_img.get_rect()
            msg_rect.top = current_y
            msg_rect.left = self.box_3.left + 10
            self.event_msg_rect.append(msg_rect)
            current_y += msg_rect.height + 5

            # 如果当前消息是“开始小游戏”按钮，则将其rect赋给 self.start_minigame_button_rect
            if gs.game_state == self.ai_settings.MINI_GAME_STARTING and i == 1: # 假设它是第二个消息
                self.start_minigame_button_rect = msg_rect
        
        # 设置“结束回合”按钮的位置 (仅在 END_ROUND 或 SHOW_MINI_GAME_RESULT 状态)
        if gs.game_state == self.ai_settings.END_ROUND or gs.game_state == self.ai_settings.SHOW_MINI_GAME_RESULT or gs.game_state ==self.ai_settings.SHOP_RESULT:
            self.button_rect.bottom = self.box_3.bottom - 10
            self.button_rect.right = self.box_3.right - 10
    
    def draw_messageboard(self, gs, pq):

        pygame.draw.rect(self.screen, self.box_color_1, self.box_1)
        pygame.draw.rect(self.screen, self.box_color_2, self.box_2)
        pygame.draw.rect(self.screen, self.box_color_3, self.box_3)

        self.update_players_message(pq) # 更新玩家信息
        for i in range(len(self.player_rendered_msgs)): # 使用更新后的列表名
            self.screen.blit(self.player_rendered_msgs[i][0], self.player_msg_rects[i][0])
            self.screen.blit(self.player_rendered_msgs[i][1], self.player_msg_rects[i][1])

        self.update_event_message(gs, pq.cur_player) # 更新事件/游戏状态信息
        for i in range(len(self.event_msg)):
            self.screen.blit(self.event_msg[i], self.event_msg_rect[i])

        # 绘制“结束回合”按钮
        if gs.game_state == self.ai_settings.END_ROUND or \
           gs.game_state == self.ai_settings.SHOW_MINI_GAME_RESULT or \
            gs.game_state == self.ai_settings.SHOP_RESULT:
            self.screen.blit(self.end_round_button, self.button_rect)

        if gs.game_state == self.ai_settings.GAME_OVER:
            self._setup_game_over_buttons()
        else:
            pygame.draw.rect(self.screen, self.box_color_1, self.box_1)
            pygame.draw.rect(self.screen, self.box_color_2, self.box_2)
            pygame.draw.rect(self.screen, self.box_color_3, self.box_3)

            self.update_players_message(pq) # 更新玩家信息
            for i in range(len(self.player_rendered_msgs)): # 使用更新后的列表名
                self.screen.blit(self.player_rendered_msgs[i][0], self.player_msg_rects[i][0])
                self.screen.blit(self.player_rendered_msgs[i][1], self.player_msg_rects[i][1])

            self.update_event_message(gs, pq.cur_player) # 更新事件/游戏状态信息
            for i in range(len(self.event_msg)):
                self.screen.blit(self.event_msg[i], self.event_msg_rect[i])

            # 绘制“结束回合”按钮
            if gs.game_state == self.ai_settings.END_ROUND or \
            gs.game_state == self.ai_settings.SHOW_MINI_GAME_RESULT:
                self.screen.blit(self.end_round_button, self.button_rect)
            
            pass
    def _setup_game_over_buttons(self):
        """设置游戏结束界面的按钮区域"""
        # 重新开始按钮区域
        self.restart_button_rect = pygame.Rect(
            self.ai_settings.screen_width//2 - 150, 
            self.ai_settings.screen_height//2 + 200, 
            120, 40
        )
        
        # 退出按钮区域  
        self.quit_button_rect = pygame.Rect(
            self.ai_settings.screen_width//2 + 30, 
            self.ai_settings.screen_height//2 + 200, 
            120, 40
        )

        