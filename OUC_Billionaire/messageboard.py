# -*- coding: utf-8 -*-

import pygame
import os
from gate import XGate,ZGate,HGate

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

        # 新增背包相关属性
        self.inventory_button_rect = None
        self.item_buttons = []  # 存储道具按钮信息

        self.player_select_buttons = []
        
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
            self.button_rect = self.end_round_button.get_rect()
            self.button_rect.bottom = self.box_3.bottom - 10
            self.button_rect.right = self.box_3.right - 10
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

    def update_inventory_message(self, player, selecting_qubit=False, selecting_gate=False, steal_mode=None, steal_target=None):
        """只更新数据，不进行绘制"""
        self.item_buttons = []
        self.qubit_buttons = []
        self.inventory_msgs = []
        self.gate_buttons = []  # 新增：量子门按钮
        
        # 背包标题
        title = f"{player.player_name}的背包 (积分: {player.score})"
        self.inventory_msgs.append(self.font.render(title, True, (30, 30, 120)))
        
        # 量子比特区域标题
        self.inventory_msgs.append(self.font.render("量子比特:", True, (60, 60, 60)))
        
        # 道具区域标题
        self.inventory_msgs.append(self.font.render("道具:", True, (60, 60, 60)))

        # 量子门区域标题 (新增)
        self.inventory_msgs.append(self.font.render("量子门:", True, (60, 60, 60)))
        
        # 存储qubit按钮信息
        for i, qubit in enumerate(player.qubits[:4]):
            self.qubit_buttons.append((i, None))  # rect在draw时确定
        
        # 存储道具按钮信息
        for i, item in enumerate(player.items[:4]):
            self.item_buttons.append((item, None))  # rect在draw时确定
        
        # 存储量子门按钮信息
        for i, item in enumerate(player.gates[:4]):
            self.gate_buttons.append((item, None))  # rect在draw时确定

        # 操作按钮状态
        self.selecting_qubit = selecting_qubit
        self.selecting_gate = selecting_gate  # 新增：选择量子门状态

        # 抢夺模式下的特殊显示
        if steal_mode == "select_player":
            prompt = "请选择要抢夺的玩家:"
            self.inventory_msgs.append(self.font.render(prompt, True, (200, 0, 0)))
            
        elif steal_mode == "select_qubit" and steal_target:
            prompt = f"选择从{steal_target.player_name}抢夺的量子比特:"
            self.inventory_msgs.append(self.font.render(prompt, True, (200, 0, 0)))

    def draw_inventory(self, gs, pq):
        """集中处理所有绘制逻辑"""
        # 背包主窗口 (居中)
        inventory_rect = pygame.Rect(
            (self.screen.get_width() - 1000) // 2,
            (self.screen.get_height() - 700) // 2,
            1000, 700
        )
        pygame.draw.rect(self.screen, (240, 240, 245), inventory_rect, border_radius=15)
        pygame.draw.rect(self.screen, (50, 50, 70), inventory_rect, width=3, border_radius=15)
        
        # ===== 绘制标题 =====
        current_y = inventory_rect.top + 20
        title_img = self.inventory_msgs[0]
        self.screen.blit(title_img, (inventory_rect.centerx - title_img.get_width()//2, current_y))
        current_y += title_img.get_height() + 30
        
        # ===== 量子比特区域 =====
        qubit_title = self.inventory_msgs[1]
        self.screen.blit(qubit_title, (inventory_rect.left + 40, current_y))
        current_y += qubit_title.get_height() + 10
        
        # 量子比特容器
        qubit_container = pygame.Rect(
            inventory_rect.left + 20,
            current_y,
            inventory_rect.width - 40,
            100
        )
        pygame.draw.rect(self.screen, (220, 240, 255), qubit_container, border_radius=10)
        pygame.draw.rect(self.screen, (100, 150, 200), qubit_container, width=2, border_radius=10)
        
        # 绘制量子比特
        for i, (qubit_idx, _) in enumerate(self.qubit_buttons):
            qubit = pq.cur_player.qubits[qubit_idx]
            qubit_rect = pygame.Rect(
                qubit_container.left + 20 + i * 220,
                qubit_container.top + 15,
                200,
                70
            )
            self.qubit_buttons[i] = (qubit_idx, qubit_rect)  # 更新rect
            
            # 绘制单个qubit框
            pygame.draw.rect(self.screen, (255, 255, 255), qubit_rect, border_radius=8)
            pygame.draw.rect(self.screen, (70, 130, 180), qubit_rect, width=1, border_radius=8)
            
            # qubit信息
            alpha_str = f"{qubit.alpha.real:.2f}".rstrip('0').rstrip('.')
            beta_str = f"{qubit.beta.real:.2f}".rstrip('0').rstrip('.')
            prob_1 = abs(qubit.beta)**2 * 100
            qubit_text = f"Q{i+1}: {alpha_str}|0> + {beta_str}|1>"
            qubit_img = self.font.render(qubit_text, True, (40, 40, 40))
            self.screen.blit(qubit_img, (qubit_rect.left + 10, qubit_rect.centery - 10))

        current_y += 110
        
        # ===== 道具区域 =====
        item_title = self.inventory_msgs[2]
        self.screen.blit(item_title, (inventory_rect.left + 40, current_y))
        current_y += item_title.get_height() + 10
        
        # 道具容器
        item_container = pygame.Rect(
            inventory_rect.left + 20,
            current_y,
            inventory_rect.width - 40,
            100
        )
        pygame.draw.rect(self.screen, (240, 240, 220), item_container, border_radius=10)
        pygame.draw.rect(self.screen, (150, 120, 100), item_container, width=2, border_radius=10)
        
        # 绘制道具
        for i, (item, _) in enumerate(self.item_buttons):
            item_rect = pygame.Rect(
                item_container.left + 20 + i * 220,
                item_container.top + 15 + i * 60,
                200,
                70
            )
            self.item_buttons[i] = (item, item_rect)  # 更新rect
            
            # 绘制道具框
            color = (255, 230, 200) if i % 2 == 0 else (255, 240, 220)
            pygame.draw.rect(self.screen, color, item_rect, border_radius=8)
            pygame.draw.rect(self.screen, (180, 120, 80), item_rect, width=1, border_radius=8)
            
            # 道具名称
            item_img = self.font.render(f"{i+1}. {item.name}", True, (80, 50, 20))
            self.screen.blit(item_img, (item_rect.left + 10, item_rect.centery - 10))
            
            # 悬停提示
            mouse_pos = pygame.mouse.get_pos()
            if item_rect.collidepoint(mouse_pos):
                # 计算文本尺寸
                desc_surface = self.font.render(item.description, True, (100, 100, 100))
                text_width, text_height = desc_surface.get_size()
                
                # 设置提示框的内边距
                padding = 10
                
                # 计算提示框的位置和大小
                tooltip_width = text_width + padding * 2
                tooltip_height = text_height + padding * 2
                
                # 确保提示框不会超出屏幕右侧
                max_x = self.screen.get_width() - tooltip_width - 10
                tooltip_x = min(item_rect.right + 10, max_x)
                
                # 确保提示框不会超出屏幕顶部和底部
                max_y = self.screen.get_height() - tooltip_height
                tooltip_y = max(10, min(mouse_pos[1] - tooltip_height // 2, max_y))
                
                tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
                
                # 绘制半透明提示框背景
                s = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
                s.fill((255, 255, 240, 230))  # 半透明白色
                self.screen.blit(s, (tooltip_x, tooltip_y))
                
                # 绘制提示框边框
                pygame.draw.rect(self.screen, (180, 120, 80), tooltip_rect, width=2, border_radius=5)
                
                # 绘制道具描述文本
                self.screen.blit(desc_surface, (tooltip_x + padding, tooltip_y + padding))
        
        current_y += 110
                
        # ===== 量子门区域 (新增) =====
        gate_title = self.inventory_msgs[3]  # 索引改为3
        self.screen.blit(gate_title, (inventory_rect.left + 40, current_y))
        current_y += gate_title.get_height() + 10
        
        # 量子门容器
        gate_container = pygame.Rect(
            inventory_rect.left + 20,
            current_y,
            inventory_rect.width - 40,
            100
        )
        pygame.draw.rect(self.screen, (240, 220, 240), gate_container, border_radius=10)
        pygame.draw.rect(self.screen, (120, 100, 120), gate_container, width=2, border_radius=10)
        
        # 绘制量子门
        for i, (gate, _) in enumerate(self.gate_buttons):
            gate_rect = pygame.Rect(
                gate_container.left + 20 + i * 200,
                gate_container.top + 15,
                180,
                70
            )
            self.gate_buttons[i] = (gate, gate_rect)  # 更新rect
            
            # 绘制量子门框
            color = (255, 240, 240) if i % 2 == 0 else (240, 240, 255)
            pygame.draw.rect(self.screen, color, gate_rect, border_radius=8)
            pygame.draw.rect(self.screen, (150, 100, 150), gate_rect, width=2, border_radius=8)
            
            # 量子门名称和描述
            gate_name = self.font.render(gate.name, True, (80, 30, 30))
            
            self.screen.blit(gate_name, (gate_rect.centerx - gate_name.get_width()//2, gate_rect.top + 15))
        
        # ===== 操作按钮 =====
        self.button_rect = pygame.Rect(
            inventory_rect.centerx - 100,
            inventory_rect.bottom - 70,
            200, 50
        )
        button_color = (100, 180, 100) if not (self.selecting_qubit or self.selecting_gate) else (180, 100, 100)
        pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (40, 80, 40), self.button_rect, width=2, border_radius=10)
        
        button_text = "继续(C)"
        if self.selecting_qubit:
            button_text = "取消选择(X)"
        elif self.selecting_gate:
            button_text = "取消选择门(X)"
            
        button_img = self.font.render(button_text, True, (255, 255, 255))
        self.screen.blit(button_img, (
            self.button_rect.centerx - button_img.get_width()//2,
            self.button_rect.centery - button_img.get_height()//2
        ))
        
        # 选择提示
        if self.selecting_qubit:
            hint_img = self.font.render("请点击要测量的量子比特", True, (200, 0, 0))
            self.screen.blit(hint_img, (
                inventory_rect.centerx - hint_img.get_width()//2,
                self.button_rect.top - 40
            ))
        elif self.selecting_gate:
            hint_img = self.font.render("请点击要应用的量子门", True, (0, 0, 200))
            self.screen.blit(hint_img, (
                inventory_rect.centerx - hint_img.get_width()//2,
                self.button_rect.top - 40
            ))
            
    def draw_player_selection(self, players, current_player):
        self.player_select_buttons = []  # 清空旧按钮
        """绘制玩家选择弹窗"""
        # 半透明背景
        s = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        
        # 弹窗主体
        popup_width, popup_height = 500, 400
        popup_rect = pygame.Rect(
            (self.screen.get_width() - popup_width) // 2,
            (self.screen.get_height() - popup_height) // 2,
            popup_width, popup_height
        )
        pygame.draw.rect(self.screen, (240, 240, 245), popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, (50, 50, 70), popup_rect, width=3, border_radius=15)
        
        # 标题
        title = self.font.render("选择要抢夺的玩家", True, (40, 40, 120))
        self.screen.blit(title, (popup_rect.centerx - title.get_width()//2, popup_rect.top + 20))
        
        # 玩家按钮 - 固定Y坐标增量
        button_y = popup_rect.top + 80  # 起始Y位置
        button_height = 60
        button_spacing = 80
        
        for player in players:
            if player == current_player:
                continue
                
            btn_rect = pygame.Rect(
                popup_rect.centerx - 150,
                button_y,  # 使用动态Y坐标，不依赖索引
                300, button_height
            )
            self.player_select_buttons.append((player, btn_rect))
            
            # 绘制按钮
            color = (200, 230, 255) if len(self.player_select_buttons) % 2 == 0 else (220, 240, 255)
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 150, 200), btn_rect, width=2, border_radius=10)
            
            # 玩家信息
            text = f"{player.player_name} (量子比特: {len(player.qubits)})"
            text_img = self.font.render(text, True, (60, 60, 60))
            self.screen.blit(text_img, (
                btn_rect.centerx - text_img.get_width()//2,
                btn_rect.centery - text_img.get_height()//2
            ))
            
            # 每次循环后更新Y坐标
            button_y += button_spacing
        
        # 取消按钮
        cancel_rect = pygame.Rect(
            popup_rect.centerx - 80,
            popup_rect.bottom - 60,
            160, 40
        )
        pygame.draw.rect(self.screen, (180, 100, 100), cancel_rect, border_radius=8)
        cancel_text = self.font.render("取消", True, (255, 255, 255))
        self.screen.blit(cancel_text, (
            cancel_rect.centerx - cancel_text.get_width()//2,
            cancel_rect.centery - cancel_text.get_height()//2
        ))
        self.cancel_select_rect = cancel_rect
        
        return cancel_rect
    
    def draw_target_qubits(self, target_player):
        """绘制目标玩家的qubit列表"""
        self.qubit_buttons = []  # 存储qubit选择按钮
        
        # 清屏或使用半透明覆盖
        s = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        
        # 弹窗
        popup_rect = pygame.Rect(
            (self.screen.get_width() - 500) // 2,
            (self.screen.get_height() - 400) // 2,
            500, 400
        )
        pygame.draw.rect(self.screen, (240, 240, 245), popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, (50, 50, 70), popup_rect, width=3, border_radius=15)
        
        # 标题
        title = self.font.render(f"选择要从{target_player.player_name}抢夺的量子比特", True, (40, 40, 120))
        self.screen.blit(title, (popup_rect.centerx - title.get_width()//2, popup_rect.top + 20))
        
        # 绘制qubit列表
        for i, qubit in enumerate(target_player.qubits):
            btn_rect = pygame.Rect(
                popup_rect.centerx - 150,
                popup_rect.top + 80 + i * 60,
                300, 80
            )
            self.qubit_buttons.append((i, btn_rect))  # 存储索引和矩形
            
            # 绘制qubit按钮
            pygame.draw.rect(self.screen, (200, 230, 255), btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, (100, 150, 200), btn_rect, width=2, border_radius=8)
            
            # 显示量子比特状态信息
            alpha_str = f"{qubit.alpha.real:.2f}" if qubit.alpha.imag == 0 else f"{qubit.alpha:.2f}"
            beta_str = f"{qubit.beta.real:.2f}" if qubit.beta.imag == 0 else f"{qubit.beta:.2f}"
            state_str = f"{alpha_str}|0> + {beta_str}|1>"
            
            # 计算测量概率
            prob_0 = abs(qubit.alpha)**2
            prob_1 = abs(qubit.beta)**2
            prob_text = f"P(|0>)={prob_0:.0%} P(|1>)={prob_1:.0%}"
            
            # 创建多行文本
            qubit_text = self.font.render(f"量子比特 {i+1}", True, (60, 60, 60))
            state_text = self.font.render(state_str, True, (80, 80, 80))
            prob_text = self.font.render(prob_text, True, (100, 100, 100))
            
            # 绘制文本
            self.screen.blit(qubit_text, (
                btn_rect.centerx - qubit_text.get_width()//2,
                btn_rect.top + 5
            ))
            self.screen.blit(state_text, (
                btn_rect.centerx - state_text.get_width()//2,
                btn_rect.top + 25
            ))
            self.screen.blit(prob_text, (
                btn_rect.centerx - prob_text.get_width()//2,
                btn_rect.top + 40
            ))
        
        # 取消按钮
        cancel_rect = pygame.Rect(
            popup_rect.centerx - 80,
            popup_rect.bottom - 60,
            160, 40
        )
        pygame.draw.rect(self.screen, (180, 100, 100), cancel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 60, 60), cancel_rect, width=2, border_radius=8)
        cancel_text = self.font.render("取消", True, (255, 255, 255))
        self.screen.blit(cancel_text, (
            cancel_rect.centerx - cancel_text.get_width()//2,
            cancel_rect.centery - cancel_text.get_height()//2
        ))
        
        self.cancel_select_rect = cancel_rect
