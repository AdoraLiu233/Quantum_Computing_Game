# -*- coding: utf-8 -*-

import sys
import pygame
from location import Location
from location import Dorm
from location import ScienceBuilding
from location import Hall
from location import Stadium
from location import MainBuilding
from location import StudyHall
from location import Gate
from location import TechnologyBuilding
from location import ArtMuseum
from location import OfficePlace
import mini_game_2
import json
from player import Player
import os
import simon
import quantum_bomb
import math
import shop

def draw_dashed_arrow(screen, color, start, end, dash_length=10, space_length=5, arrow_size=10):
    # 向量差
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.hypot(dx, dy)
    angle = math.atan2(dy, dx)

    # 单位向量
    x_unit = math.cos(angle)
    y_unit = math.sin(angle)

    # 虚线部分
    drawn = 0
    while drawn + dash_length < distance - arrow_size:
        start_x = start[0] + x_unit * drawn
        start_y = start[1] + y_unit * drawn
        end_x = start[0] + x_unit * (drawn + dash_length)
        end_y = start[1] + y_unit * (drawn + dash_length)
        pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 2)
        drawn += dash_length + space_length

    # 箭头部分
    # 箭头基准角度是主线角度 + 120° 和 -120°
    arrow_tip = end
    left_angle = angle + math.radians(150)
    right_angle = angle - math.radians(150)

    left_point = (
        arrow_tip[0] + math.cos(left_angle) * arrow_size,
        arrow_tip[1] + math.sin(left_angle) * arrow_size,
    )
    right_point = (
        arrow_tip[0] + math.cos(right_angle) * arrow_size,
        arrow_tip[1] + math.sin(right_angle) * arrow_size,
    )

    pygame.draw.polygon(screen, color, [arrow_tip, left_point, right_point])


def update_screen(ai_settings, screen, gs, play_button, locations,
                  location_points, messageboard, dice, pq):
    """更新屏幕上的图像，并切换到新屏幕"""
    screen.fill(ai_settings.bg_color)
    if gs.game_active:
        if gs.game_state == ai_settings.MINI_GAME_ACTIVE:
            # 小游戏活动时，屏幕更新由小游戏本身负责。
            pass # 假设小游戏会自己刷新整个屏幕
        elif gs.game_state == ai_settings.SHOP_ACTIVE:
            # 绘制商店界面

            # screen.blit(ai_settings.shop_image, (0, 0))
            pass

            
        elif gs.game_state == ai_settings.GAME_OVER:
            # 显示游戏结束界面
            draw_game_over_screen(screen, ai_settings, gs, pq)

            

        elif gs.game_state in (ai_settings.GET_QUBIT, ai_settings.GET_ITEM):
            scaled_bg = pygame.transform.scale(ai_settings.get_qubit_item_image, 
                                      (ai_settings.screen_width, ai_settings.screen_height))
            screen.blit(scaled_bg, (0, 0))
            # 绘制奖励信息
            _draw_reward_message(ai_settings,gs, screen, messageboard)

        else:
            # 绘制地图等主游戏元素
            screen.blit(ai_settings.map, (0, 0))
            for location in locations:
                location.draw_location()
            # pygame.draw.lines(screen, ai_settings.line_color, True, location_points, 3)
            for i in range(len(location_points)):
                start = location_points[i]
                end = location_points[(i + 1) % len(location_points)]  # 闭环
                draw_dashed_arrow(screen, (0, 0, 0), start, end)
            # print(f"Player {pq.cur_player.player_name}'s pos: ", pq.cur_player.pos)
            pq.reverse_draw() # 绘制玩家
            messageboard.draw_messageboard(gs, pq)
            # if gs.game_state == ai_settings.ROLL_DICE : # 只在掷骰子阶段画骰子
            dice.draw_dice(dice.cur_dice)
            draw_round_info(screen, ai_settings, gs)

    else: # 游戏未激活
        screen.blit(ai_settings.bg_image, (0, 0))
        play_button.draw_button()

    pygame.display.flip()


def draw_round_info(screen, ai_settings, gs):
    """在屏幕上显示当前回合信息"""
    font = pygame.font.Font(None, 36)
    round_text = f"Round: {gs.current_round}/{gs.max_rounds}"
    text_surface = font.render(round_text, True, (255, 255, 255))
    
    # 在屏幕右上角显示回合信息
    text_rect = text_surface.get_rect()
    text_rect.topright = (ai_settings.screen_width - 20, 20)
    screen.blit(text_surface, text_rect)

def draw_game_over_screen(screen, ai_settings, gs, pq):
    """绘制美化版游戏结束界面"""
    
    # 创建半透明背景 - 浅紫色
    overlay = pygame.Surface((ai_settings.screen_width, ai_settings.screen_height))
    overlay.set_alpha(180)
    overlay.fill((130, 120, 180))  # 浅紫色背景
    screen.blit(overlay, (0, 0))
    
    # 添加边框装饰 - 白色边框
    border_rect = pygame.Rect(60, 60, ai_settings.screen_width - 120, ai_settings.screen_height - 120)
    pygame.draw.rect(screen, (255, 255, 255), border_rect, 4)
    
    # 内部装饰边框 - 浅紫色
    inner_border = pygame.Rect(70, 70, ai_settings.screen_width - 140, ai_settings.screen_height - 140)
    pygame.draw.rect(screen, (180, 170, 220), inner_border, 2)
    
    # 加载字体
    font_large = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 72)
    font_medium = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 48)
    font_small = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 36)
    
    # 游戏结束标题 - 白色
    game_over_text = font_large.render("游戏结束", True, (255, 255, 255))
    game_over_rect = game_over_text.get_rect(center=(ai_settings.screen_width//2, 150))
    screen.blit(game_over_text, game_over_rect)
    
    # 装饰线 - 白色
    line_y = 190
    pygame.draw.line(screen, (255, 255, 255), 
                    (ai_settings.screen_width//2 - 120, line_y), 
                    (ai_settings.screen_width//2 + 120, line_y), 3)
    
    # 装饰小矩形
    for i in range(3):
        rect_x = ai_settings.screen_width//2 - 30 + i * 30
        pygame.draw.rect(screen, (255, 255, 255), (rect_x, line_y + 10, 15, 15))
    
    # 显示最终结果 - 浅紫色
    final_round_text = font_medium.render(f"总共进行了 {gs.max_rounds} 回合", True, (220, 210, 255))
    final_round_rect = final_round_text.get_rect(center=(ai_settings.screen_width//2, 250))
    screen.blit(final_round_text, final_round_rect)
    
    # 排名区域
    ranking_start_y = 320
    sorted_players = sorted(pq.queue, key=lambda p: p.money, reverse=True)
    ranking_height = 80 + len(sorted_players) * 45
    
    # 排名背景框 - 白色背景
    ranking_rect = pygame.Rect(ai_settings.screen_width//2 - 280, ranking_start_y - 20, 560, ranking_height)
    pygame.draw.rect(screen, (255, 255, 255), ranking_rect)
    
    # 排名框边框 - 浅紫色
    pygame.draw.rect(screen, (160, 140, 200), ranking_rect, 3)
    
    # 排名标题背景条 - 浅紫色
    title_bg_rect = pygame.Rect(ai_settings.screen_width//2 - 280, ranking_start_y - 20, 560, 50)
    pygame.draw.rect(screen, (180, 170, 220), title_bg_rect)
    
    # 排名标题 - 白色字体
    ranking_title = font_medium.render("最终排名", True, (255, 255, 255))
    ranking_title_rect = ranking_title.get_rect(center=(ai_settings.screen_width//2, ranking_start_y + 5))
    screen.blit(ranking_title, ranking_title_rect)
    
    # 显示玩家排名 - 不同深浅的紫色
    rank_colors = [
        (80, 60, 120),    # 深紫色 - 第一名
        (110, 90, 150),   # 中紫色 - 第二名
        (140, 120, 180),  # 浅紫色 - 第三名
        (100, 80, 140)    # 紫色 - 其他
    ]
    
    for i, player in enumerate(sorted_players):
        color = rank_colors[min(i, 3)]
        
        # 排名序号背景
        rank_bg_rect = pygame.Rect(ai_settings.screen_width//2 - 260, ranking_start_y + 40 + i*40, 40, 35)
        pygame.draw.rect(screen, color, rank_bg_rect)
        
        # 排名序号
        rank_num = font_small.render(f"{i+1}", True, (255, 255, 255))
        rank_num_rect = rank_num.get_rect(center=rank_bg_rect.center)
        screen.blit(rank_num, rank_num_rect)
        
        # 玩家信息
        player_info = font_small.render(f"{player.player_name}: ${player.money}", True, color)
        player_rect = player_info.get_rect(left=ai_settings.screen_width//2 - 210, 
                                         centery=ranking_start_y + 57 + i*40)
        screen.blit(player_info, player_rect)
    
    # 退出提示区域背景 - 浅紫色
    quit_bg_y = ranking_start_y + ranking_height + 30
    quit_bg_rect = pygame.Rect(ai_settings.screen_width//2 - 150, quit_bg_y, 300, 50)
    pygame.draw.rect(screen, (200, 190, 230), quit_bg_rect)
    pygame.draw.rect(screen, (255, 255, 255), quit_bg_rect, 2)
    
    # 退出提示 - 深紫色
    quit_text = font_small.render("点击x退出游戏", True, (80, 60, 120))
    quit_rect = quit_text.get_rect(center=(ai_settings.screen_width//2, quit_bg_y + 25))
    screen.blit(quit_text, quit_rect)

def _draw_reward_message(ai_settings, gs, screen, messageboard):
    """绘制奖励详细信息"""
    popup_width, popup_height = 500, 300
    popup_rect = pygame.Rect(
        (ai_settings.screen_width - popup_width) // 2,
        (ai_settings.screen_height - popup_height) // 2,
        popup_width,
        popup_height
    )

    # 绘制弹窗背景 (带圆角和阴影效果)
    pygame.draw.rect(screen, (240, 240, 245), popup_rect, border_radius=15)
    pygame.draw.rect(screen, (50, 50, 70), popup_rect, width=3, border_radius=15)
    
    # 添加装饰性元素
    pygame.draw.line(screen, (100, 150, 200), 
                    (popup_rect.left + 30, popup_rect.top + 70),
                    (popup_rect.right - 30, popup_rect.top + 70), 3)

    # 确定消息内容
    if gs.game_state == ai_settings.GET_QUBIT:
        title = "获得量子比特"
        qubit = gs.reward_data["content"]
        alpha_str = f"{qubit.alpha.real:.2f}".rstrip('0').rstrip('.')
        beta_str = f"{qubit.beta.real:.2f}".rstrip('0').rstrip('.')
        prob_1 = abs(qubit.beta)**2 * 100
        title_surf = ai_settings.reward_font_large.render(title, True, (30, 30, 120))
        screen.blit(title_surf, (popup_rect.centerx - title_surf.get_width()//2, popup_rect.top + 20))
        
        state_text = f"量子态: {alpha_str}|0> + {beta_str}|1>"
        state_surf = ai_settings.reward_font_small.render(state_text, True, (60, 60, 60))
        screen.blit(state_surf, (popup_rect.centerx - state_surf.get_width()//2, popup_rect.top + 120))
        
        prob_text = f"测量结果为1的概率: {prob_1:.1f}%"
        prob_surf = ai_settings.reward_font_small.render(prob_text, True, (60, 60, 60))
        screen.blit(prob_surf, (popup_rect.centerx - prob_surf.get_width()//2, popup_rect.top + 160))

    elif gs.game_state == ai_settings.GET_ITEM:
        title = "获得道具"
        item = gs.reward_data["content"]
        title_surf = ai_settings.reward_font_large.render(title, True, (30, 30, 120))
        screen.blit(title_surf, (popup_rect.centerx - title_surf.get_width()//2, popup_rect.top + 20))
        
        name_text = f"名称: {item.name}"
        name_surf = ai_settings.reward_font_small.render(name_text, True, (60, 60, 60))
        screen.blit(name_surf, (popup_rect.centerx - name_surf.get_width()//2, popup_rect.top + 120))
        
        desc_lines = _wrap_text(item.description, ai_settings.reward_font_small, popup_width - 100)
        for i, line in enumerate(desc_lines):
            desc_surf = ai_settings.reward_font_small.render(line, True, (80, 80, 80))
            screen.blit(desc_surf, (popup_rect.centerx - desc_surf.get_width()//2, popup_rect.top + 160 + i*20))
    else:
        return

    # 绘制确认按钮 (美观样式)
    button_rect = pygame.Rect(
        popup_rect.centerx - 80,
        popup_rect.bottom - 70,
        160, 50
    )
    
    # 按钮交互效果
    mouse_pos = pygame.mouse.get_pos()
    button_color = (100, 180, 100) if button_rect.collidepoint(mouse_pos) else (70, 150, 70)
    
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
    pygame.draw.rect(screen, (40, 80, 40), button_rect, width=2, border_radius=10)
    
    confirm_text = ai_settings.reward_font_small.render("确认", True, (255, 255, 255))
    screen.blit(confirm_text, (
        button_rect.centerx - confirm_text.get_width()//2,
        button_rect.centery - confirm_text.get_height()//2
    ))
    
    # 更新messageboard的按钮位置
    messageboard.button_rect = button_rect

def _wrap_text(text, font, max_width):
    """将长文本自动换行"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def check_events(ai_settings, gs, play_button, locations, messageboard, dice, pq, screen):
    """监视并相应鼠标和键盘事件"""
    if gs.game_state == ai_settings.MINI_GAME_ACTIVE:
        # 小游戏通常有自己的事件处理循环。
        return # 主事件循环暂时不处理，等待小游戏结束

    for event in pygame.event.get():
        # 退出事件
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if dice._handle_secret_control(event):
            continue

        if event.type == pygame.MOUSEBUTTONDOWN:
            # 确保在调用 check_click_events 之前游戏是激活的
            if gs.game_active:
                 check_click_events(ai_settings, gs, play_button, locations,
                                   messageboard, dice, pq, screen)
            elif play_button.img_rect.collidepoint(pygame.mouse.get_pos()): # 处理游戏未激活时点击开始按钮
                 check_click_events(ai_settings, gs, play_button, locations,
                                   messageboard, dice, pq, screen)

def check_click_events(ai_settings, gs, play_button, locations, messageboard, dice, pq, screen):
    """处理鼠标点击事件的函数"""
    # 定位鼠标点击位置
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if not gs.game_active:
        if play_button.img_rect.collidepoint(mouse_x, mouse_y):
            gs.game_active = True
            gs.game_state = ai_settings.ROLL_DICE # 游戏开始，准备掷骰子
        return # 如果游戏未激活，则不处理其他点击
    
    if gs.is_game_over():
        gs.game_state = ai_settings.GAME_OVER
        return
                

    # 游戏激活后的点击事件处理
    if gs.game_state == ai_settings.ROLL_DICE:
        if dice.rect.collidepoint(mouse_x, mouse_y):
            step = dice.roll_dice()
            # print(f"Player num:{}")
            print(f"Player {pq.cur_player.player_name} rolled a {step}.")
            print(f"Player {pq.cur_player.player_name} is at {pq.cur_player.pos}.")
            pq.cur_player.move(step)
            current_loc = locations[pq.cur_player.pos]
            print(f"Player {pq.cur_player.player_name} moved to {current_loc.name}.")
            gs.cur_event_index = current_loc.trigger_event(pq.cur_player) # cur_event_index 现在可以是字符串

            gs.mini_game_result_message = "" # 重置小游戏结果
            gs.shop_result_message = "" # 重置商店结果

            if gs.cur_event_index == "TRIGGER_MINI_GAME":
                gs.current_mini_game_id = current_loc.mini_game_id
                gs.game_state = ai_settings.MINI_GAME_STARTING # 进入小游戏准备阶段
                # print(f"Player {pq.cur_player.player_name} landed on a minigame: {gs.current_mini_game_id}")
            elif gs.cur_event_index == "TRIGGER_SHOP":
                print("-------------------------enter shop-------------------------")

                gs.game_state = ai_settings.SHOP_ENTERING

                
            elif gs.cur_event_index == "GET_RANDOM_QUBIT":
                new_qubit = current_loc.get_random_qubit()
                pq.cur_player.add_qubit(new_qubit)

                # 准备详细消息
                alpha_str = f"{new_qubit.alpha.real:.2f}"
                beta_str = f"{new_qubit.beta.real:.2f}"
                gs.reward_data = {
                    "type": "qubit",
                    "content": new_qubit
                }
                gs.game_state = ai_settings.GET_QUBIT
            elif gs.cur_event_index == "GET_RANDOM_ITEM":
                new_item = current_loc.get_random_item()
                pq.cur_player.items.append(new_item)
                gs.reward_data = {
                    "type": "item",
                    "content": new_item
                }
                gs.game_state = ai_settings.GET_ITEM

            elif isinstance(gs.cur_event_index, int): # 是普通事件索引
                print("无事发生")
                gs.game_state = ai_settings.END_ROUND
            else:
                print(f"Warning: Unknown event index type: {gs.cur_event_index}")
                gs.game_state = ai_settings.END_ROUND
    elif gs.game_state == ai_settings.SHOP_ENTERING:
        run_shop(ai_settings, screen, gs, pq.cur_player)
        gs.game_state = ai_settings.END_ROUND

    elif gs.game_state == ai_settings.MINI_GAME_STARTING:
        # 这个状态下，通常 Messageboard 会显示 "点击开始小游戏" 或类似按钮
        # 假设 Messageboard 有一个 start_minigame_button_rect
        if messageboard.start_minigame_button_rect and \
           messageboard.start_minigame_button_rect.collidepoint(mouse_x, mouse_y):
            gs.game_state = ai_settings.MINI_GAME_ACTIVE
            # 在这里，主游戏循环会将控制权（部分或全部）交给小游戏模块
            run_specific_mini_game(ai_settings, screen, gs, pq.cur_player)
        # 如果没有点击开始按钮，则停留在 MINI_GAME_STARTING 状态

    elif gs.game_state == ai_settings.SHOW_MINI_GAME_RESULT:
        # 显示小游戏结果后，等待玩家点击“结束回合”按钮
        if messageboard.button_rect.collidepoint(mouse_x, mouse_y):
            gs.mini_game_result_message = "" # 清理结果
            gs.mini_game_player_effect = None
            gs.current_mini_game_id = None
            pq.next_round()

            if pq.is_round_completed():
                gs.increment_round()
            if pq.is_round_completed():
                gs.increment_round()
                print(f"Round {gs.current_round - 1} completed! Starting round {gs.current_round}")
            
            # 检查游戏是否结束
            if gs.is_game_over():
                gs.game_state = ai_settings.GAME_OVER
            else:
                gs.game_state = ai_settings.ROLL_DICE

    # 处理商店逻辑
    elif gs.game_state == ai_settings.SHOP_RESULT:
        # 处理商店点击事件
        if messageboard.button_rect.collidepoint(mouse_x, mouse_y):
            gs.mini_game_result_message = "" # 清理结果
            gs.mini_game_player_effect = None
            gs.current_mini_game_id = None
            pq.next_round()
            gs.game_state = ai_settings.ROLL_DICE # 返回掷骰子状态
            # 这里可以添加商店逻辑，例如购买物品等
    # 处理获得qubit/item逻辑
    elif gs.game_state in (ai_settings.GET_QUBIT, ai_settings.GET_ITEM):
        if messageboard.button_rect.collidepoint(mouse_x, mouse_y):
            gs.game_state = ai_settings.ROLL_DICE
            pq.next_round()
    elif gs.game_state == ai_settings.END_ROUND:
        if messageboard.button_rect.collidepoint(mouse_x, mouse_y):
            # 切换玩家
            pq.next_round()
            
            # 检查是否完成一轮，如果是则增加回合数
            if pq.is_round_completed():
                gs.increment_round()
                print(f"Round {gs.current_round - 1} completed! Starting round {gs.current_round}")
            
            # 检查游戏是否结束
            if gs.is_game_over():
                gs.game_state = ai_settings.GAME_OVER
            else:
                gs.game_state = ai_settings.ROLL_DICE
                
    elif gs.game_state == ai_settings.GAME_OVER:
            pygame.quit()
            sys.exit()

def create_location(ai_settings, screen, locations, index, x, y, name, mini_game_id):
    """创建一个地点"""
    if name == "宿舍区":
        location = Dorm(ai_settings, screen, index, x, y, name, mini_game_id)
    elif name == "理科楼":
        location = ScienceBuilding(ai_settings, screen, index, x, y, name, mini_game_id)
    elif name == "工字厅":
        location = OfficePlace(ai_settings, screen, index, x, y, name, mini_game_id)
    elif name == "大礼堂":
        location = Hall(ai_settings, screen, index, x, y, name, mini_game_id)
    elif name == "综合体育馆":
        location = Stadium(ai_settings, screen, index, x, y, name, mini_game_id)
    elif name == "清华主楼":
        location = MainBuilding(ai_settings, screen, index, x, y, name, mini_game_id)
    elif name == "清华学堂":
        location = StudyHall(ai_settings, screen, index, x, y, name, mini_game_id)
    elif name == "科技楼":
        location = TechnologyBuilding(ai_settings, screen, index, x, y, name, mini_game_id)
    elif name == "艺术博物馆":
        location = ArtMuseum(ai_settings, screen, index, x, y, name, mini_game_id)
    elif name == "二校门":
        location = Gate(ai_settings, screen, index, x, y, name, mini_game_id)
    else:
        location = Location(ai_settings, screen, index, x, y, name, mini_game_id)
    locations.append(location)

def create_all_locations(ai_settings, screen, locations, location_points):
    """创建所有的地点圆点"""
    data = read_locations_list(ai_settings)
    ai_settings.location_cnt = len(data)
    for i in range(0, ai_settings.location_cnt):
        create_location(ai_settings, screen, locations, i, int(data[i][0]), 
                        int(data[i][1]), data[i][2], data[i][3])
        location_points.append([int(data[i][0]), int(data[i][1])])
    ai_settings.locations_instance_list = locations
        
def read_locations_list(ai_settings):
    """从txt文件中读取地点信息"""
    data = []
    with open(ai_settings.locations_data_path, encoding = ('utf-8')) as file_data:
        for line in file_data:
            line = line.rstrip()
            parts = line.split(' ')
            x, y, name = parts[0], parts[1], parts[2]
            mini_game_id = parts[3] if len(parts) > 3 and parts[3].lower() != 'none' else None
            data.append([x, y, name, mini_game_id])
    return data

def read_events_list(ai_settings):
    """从json文件中读取事件信息"""
    with open(ai_settings.events_path, encoding = ('utf-8')) as file:
        events_dict = json.load(file)
        #print(events_dict)
        # 更新事件总数
        ai_settings.event_cnt = len(events_dict['events'])
        return events_dict['events']

def run_specific_mini_game(ai_settings, screen, gs, current_player):
    """
    根据 gs.current_mini_game_id 调用并运行相应的小游戏。
    小游戏应该处理自己的事件循环和屏幕绘制。
    """
    original_caption = pygame.display.get_caption()
    game_id_for_title = gs.current_mini_game_id if gs.current_mini_game_id else "未知游戏"
    pygame.display.set_caption(f"小游戏: {game_id_for_title}")

    game_result = {"message": f"小游戏 '{game_id_for_title}' 未实现或配置错误。", "effect": 0}

    if gs.current_mini_game_id == "simon":
        game_result = simon.play(screen, ai_settings, current_player)
    elif gs.current_mini_game_id == "quantum_bomb":
        game_result = quantum_bomb.play(screen, ai_settings, current_player)
    elif gs.current_mini_game_id == "mini_game_2":
        game_result = mini_game_2.play(screen, gs, ai_settings)
    else:
        print(f"Warning: Attempted to run unknown or unhandled minigame ID '{gs.current_mini_game_id}'")
        # Fallback message already set in game_result init

    gs.mini_game_result_message = game_result["message"]
    gs.mini_game_player_effect = game_result["effect"] # Store the effect
    current_player.money += game_result["effect"] # Apply the effect to the player

    # Apply the effect to the player
    if isinstance(gs.mini_game_player_effect, (int, float)):
        current_player.invest(gs.mini_game_player_effect)
    else:
        print(f"Warning: Minigame effect '{gs.mini_game_player_effect}' is not a number.")

    pygame.display.set_caption(original_caption[0])
    gs.game_state = ai_settings.SHOW_MINI_GAME_RESULT


def run_shop(ai_settings, screen, gs, current_player):
    """
    根据 gs.current_mini_game_id 调用并运行相应的小游戏。
    小游戏应该处理自己的事件循环和屏幕绘制。
    """
    original_caption = pygame.display.get_caption()
    game_id_for_title = gs.current_mini_game_id if gs.current_mini_game_id else "未知游戏"
    pygame.display.set_caption(f"小游戏: {game_id_for_title}")

    shop_result = {"message": f"小游戏 '{game_id_for_title}' 未实现或配置错误。", "effect": 0}
    print("2222222222222")
    shop_result = shop.play(screen, ai_settings, current_player)
    print("333333333333333")
   

    gs.shop_result_message = shop_result["message"]
    gs.shop_cost = shop_result["cost"] # Store the effect
    print(f"Shop result message: {gs.shop_result_message}, cost: {gs.shop_cost}")
    current_player.money-=gs.shop_cost  # 扣除玩家金钱
    # Apply the effect to the player
    

    pygame.display.set_caption(original_caption[0])
    gs.game_state = ai_settings.SHOP_RESULT

def create_player_queue(ai_settings, screen, locations, pq):
    # 创建所有玩家
    player1 = Player(ai_settings, screen, locations, 1, "红色小人")
    player2 = Player(ai_settings, screen, locations, 2, "橙色小人")
    player3 = Player(ai_settings, screen, locations, 3, "蓝色小人")
    # 将所有玩家加入游戏队列
    pq.add_player(player1)
    pq.add_player(player2)
    pq.add_player(player3)