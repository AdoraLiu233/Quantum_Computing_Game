# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 22:05:22 2019

@author: Sherlock Holmes
"""

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
import json
from player import Player
import os
import mini_game_reaction
import math

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
                  location_points, event_imgs, messageboard, dice, pq): # 删除了 events_dict，messageboard 自己有
    """更新屏幕上的图像，并切换到新屏幕"""
    screen.fill(ai_settings.bg_color)
    if gs.game_active:
        if gs.game_state == ai_settings.MINI_GAME_ACTIVE:
            # 小游戏活动时，屏幕更新由小游戏本身负责。
            # 此处可以什么都不画，或者画一个简单的“小游戏进行中”的提示。
            # font = pygame.font.SysFont('SimHei', 50)
            # text = font.render("小游戏进行中...", True, (0,0,0))
            # text_rect = text.get_rect(center=screen.get_rect().center)
            # screen.blit(text, text_rect)
            pass # 假设小游戏会自己刷新整个屏幕
        elif gs.game_state == ai_settings.SHOP:
            # 绘制商店界面
            screen.blit(ai_settings.shop_image, (0, 0))
            # messageboard.draw_messageboard(gs, event_imgs, pq)
        else:
            # 绘制地图等主游戏元素
            screen.blit(ai_settings.map, (0, 0))
            for location in locations:
                location.draw_location()
            pygame.draw.lines(screen, ai_settings.line_color, True, location_points, 3)
            pq.reverse_draw() # 绘制玩家
            messageboard.draw_messageboard(gs, event_imgs, pq) # 绘制信息板 (event_imgs可能用不到了，看gs.cur_event_imgs)
            # if gs.game_state == ai_settings.ROLL_DICE : # 只在掷骰子阶段画骰子
            dice.draw_dice(dice.cur_dice)
    else: # 游戏未激活
        screen.blit(ai_settings.bg_image, (0, 0))
        play_button.draw_button()

    pygame.display.flip()

def check_events(ai_settings, gs, play_button, locations, events_dict, 
                 events_imgs, messageboard, dice, pq):
    """监视并相应鼠标和键盘事件"""
    if gs.game_state == ai_settings.MINI_GAME_ACTIVE:
        # 小游戏通常有自己的事件处理循环。
        # 如果小游戏不是阻塞式的，你可能需要在这里传递事件给小游戏：
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT: # 全局退出还是要处理
        #         pygame.quit()
        #         sys.exit()
        #     # current_active_minigame.handle_event(event)
        # 或者，如果小游戏是阻塞的（如下面 run_specific_mini_game 所示），则这里不需要做什么特别的。
        # 只需要确保QUIT事件能被小游戏内部的循环捕获并正确退出。
        # 为了简单起见，我们假设小游戏会处理自己的QUIT。
        return # 主事件循环暂时不处理，等待小游戏结束

    for event in pygame.event.get():
        # 退出事件
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 确保在调用 check_click_events 之前游戏是激活的
            if gs.game_active:
                 check_click_events(ai_settings, gs, play_button, locations,
                                   events_dict, events_imgs, messageboard, dice, pq)
            elif play_button.img_rect.collidepoint(pygame.mouse.get_pos()): # 处理游戏未激活时点击开始按钮
                 check_click_events(ai_settings, gs, play_button, locations,
                                   events_dict, events_imgs, messageboard, dice, pq)

def check_click_events(ai_settings, gs, play_button, locations, events_dict, 
                       events_imgs, messageboard, dice, pq):
    """处理鼠标点击事件的函数"""
    # 定位鼠标点击位置
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if not gs.game_active:
        if play_button.img_rect.collidepoint(mouse_x, mouse_y):
            gs.game_active = True
            gs.game_state = ai_settings.ROLL_DICE # 游戏开始，准备掷骰子
        return # 如果游戏未激活，则不处理其他点击

    # 游戏激活后的点击事件处理
    if gs.game_state == ai_settings.ROLL_DICE:
        if dice.rect.collidepoint(mouse_x, mouse_y):
            step = dice.roll_dice()
            # print(f"Player num:{}")
            print(f"Player {pq.cur_player.player_name} rolled a {step}.")
            pq.cur_player.move(step)
            current_loc = locations[pq.cur_player.pos]
            print(f"Player {pq.cur_player.player_name} moved to {current_loc.name}.")
            gs.cur_event_index = current_loc.trigger_event(pq.cur_player) # cur_event_index 现在可以是字符串

            gs.cur_event_imgs = None # 重置事件图片
            gs.mini_game_result_message = "" # 重置小游戏结果

            if gs.cur_event_index == "TRIGGER_MINI_GAME":
                gs.current_mini_game_id = current_loc.mini_game_id
                gs.game_state = ai_settings.MINI_GAME_STARTING # 进入小游戏准备阶段
                # 此处可以给messageboard发消息，例如 "即将开始小游戏：xxx"
                # print(f"Player {pq.cur_player.player_name} landed on a minigame: {gs.current_mini_game_id}")
            elif gs.cur_event_index == "TRIGGER_SHOP":
                print("-------------------------enter shop-------------------------")
                gs.game_state = ai_settings.SHOP
            elif isinstance(gs.cur_event_index, int): # 是普通事件索引
                if 0 <= gs.cur_event_index < len(events_dict) and 0 <= gs.cur_event_index < len(events_imgs):
                    gs.cur_event_imgs = events_imgs[gs.cur_event_index]
                    if events_dict[gs.cur_event_index]['type'] == "multiple_choice":
                        gs.game_state = ai_settings.CHOOSE
                    else:
                        pq.cur_player.invest(events_dict[gs.cur_event_index]['change'])
                        gs.game_state = ai_settings.END_ROUND
                else:
                    print(f"Error: Event index {gs.cur_event_index} out of bounds or invalid event data.")
                    gs.game_state = ai_settings.END_ROUND # 出错则直接结束回合
            else:
                print(f"Warning: Unknown event index type: {gs.cur_event_index}")
                gs.game_state = ai_settings.END_ROUND

    elif gs.game_state == ai_settings.CHOOSE:
        # ... (保持你现有的CHOOSE逻辑) ...
        # 选择后，设置 gs.game_state = ai_settings.END_ROUND
        chosen = False
        if messageboard.event_msg_rect[1].collidepoint(mouse_x, mouse_y):
            gs.cur_event_imgs = gs.cur_event_imgs['A']
            pq.cur_player.invest(events_dict[gs.cur_event_index]['A']['change'])
            chosen = True
        elif messageboard.event_msg_rect[2].collidepoint(mouse_x, mouse_y):
            gs.cur_event_imgs = gs.cur_event_imgs['B']
            pq.cur_player.invest(events_dict[gs.cur_event_index]['B']['change'])
            chosen = True
        elif messageboard.event_msg_rect[3].collidepoint(mouse_x, mouse_y):
            gs.cur_event_imgs = gs.cur_event_imgs['C']
            pq.cur_player.invest(events_dict[gs.cur_event_index]['C']['change'])
            chosen = True

        if chosen:
            gs.game_state = ai_settings.END_ROUND
        else: #没点到选项
            return


    elif gs.game_state == ai_settings.MINI_GAME_STARTING:
        # 这个状态下，通常 Messageboard 会显示 "点击开始小游戏" 或类似按钮
        # 假设 Messageboard 有一个 start_minigame_button_rect
        if messageboard.start_minigame_button_rect and \
           messageboard.start_minigame_button_rect.collidepoint(mouse_x, mouse_y):
            gs.game_state = ai_settings.MINI_GAME_ACTIVE
            # 在这里，主游戏循环会将控制权（部分或全部）交给小游戏模块
            # 小游戏模块执行完毕后，会设置 gs.mini_game_result_message 和 gs.game_state
            # screen 对象需要传递给小游戏函数
            # run_specific_mini_game(ai_settings, screen, gs, pq.cur_player) # 这是下一步要创建的
        # 如果没有点击开始按钮，则停留在 MINI_GAME_STARTING 状态

    elif gs.game_state == ai_settings.SHOW_MINI_GAME_RESULT:
        # 显示小游戏结果后，等待玩家点击“结束回合”按钮
        if messageboard.button_rect.collidepoint(mouse_x, mouse_y):
            # （可选）根据 gs.mini_game_player_effect 应用小游戏结果带来的实际影响
            # if gs.mini_game_player_effect is not None:
            #     pq.cur_player.invest(gs.mini_game_player_effect)

            gs.mini_game_result_message = "" # 清理结果
            gs.mini_game_player_effect = None
            gs.current_mini_game_id = None
            gs.cur_event_imgs = None
            pq.next_round()
            gs.game_state = ai_settings.ROLL_DICE
    # 处理商店逻辑
    elif gs.game_state == ai_settings.SHOP:
        # 处理商店点击事件
        if messageboard.shop_button_rect.collidepoint(mouse_x, mouse_y):
            gs.game_state = ai_settings.ROLL_DICE # 返回掷骰子状态
            # 这里可以添加商店逻辑，例如购买物品等

    elif gs.game_state == ai_settings.END_ROUND:
        if messageboard.button_rect.collidepoint(mouse_x, mouse_y):
            gs.cur_event_imgs = None
            pq.next_round()
            gs.game_state = ai_settings.ROLL_DICE

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

def read_event_images(ai_settings):
    """从event_images目录下读取所有的事件图片并存入一个列表"""
    event_images = []
    dir_path = ai_settings.event_images_dir
    dir_cnt = 0
    # 计算文件夹数量
    for name in os.listdir(dir_path):
        sub_path = os.path.join(dir_path, name)
        if os.path.isdir(sub_path):
            dir_cnt += 1
    #print("dir_cnt: " + str(dir_cnt))
    # 遍历所有文件夹
    for i in range(0, dir_cnt):
        event_dir_path = dir_path + "/event_" + str(i).zfill(3)
        file_cnt = 0
        # 计算文件数量
        for name in os.listdir(event_dir_path):
            sub_path = os.path.join(event_dir_path, name)
            if os.path.isfile(sub_path):
                file_cnt += 1
        # 如果目录下只有一个文件，则视为固定结果事件文件夹处理
        if file_cnt == 1:
            img_result = pygame.image.load((event_dir_path + "/result.png"))
            event_dict = dict({
                'result': img_result
                })
            event_images.append(event_dict)
        # 如果目录下有三个文件，则视为随机结果事件文件夹处理
        elif file_cnt == 3:
            img_result_a = pygame.image.load((event_dir_path + "/result_A.png"))
            img_result_b = pygame.image.load((event_dir_path + "/result_B.png"))
            img_result_c = pygame.image.load((event_dir_path + "/result_C.png"))
            event_dict = dict({
                'A': {'result': img_result_a},
                'B': {'result': img_result_b},
                'C': {'result': img_result_c}
                })
            event_images.append(event_dict)
        # 如果目录下有七个文件，则视为多项选择事件文件夹处理
        elif file_cnt == 7:
            img_content = pygame.image.load((event_dir_path + "/content.png"))
            img_choice_a = pygame.image.load((event_dir_path + "/choice_A.png"))
            img_choice_b = pygame.image.load((event_dir_path + "/choice_B.png"))
            img_choice_c = pygame.image.load((event_dir_path + "/choice_C.png"))
            img_result_a = pygame.image.load((event_dir_path + "/result_A.png"))
            img_result_b = pygame.image.load((event_dir_path + "/result_B.png"))
            img_result_c = pygame.image.load((event_dir_path + "/result_C.png"))
            event_dict = dict({
                    'content': img_content, 
                    'A': {'choice': img_choice_a, 'result': img_result_a},
                    'B': {'choice': img_choice_b, 'result': img_result_b},
                    'C': {'choice': img_choice_c, 'result': img_result_c}
                    })
            event_images.append(event_dict)
    #print(len(event_images))
    return event_images

def run_specific_mini_game(ai_settings, screen, gs, current_player):
    """
    根据 gs.current_mini_game_id 调用并运行相应的小游戏。
    小游戏应该处理自己的事件循环和屏幕绘制。
    小游戏结束后，需要设置:
    - gs.mini_game_result_message (例如 "游戏胜利！")
    - gs.mini_game_player_effect (例如 玩家金钱变化值)
    - gs.game_state = ai_settings.SHOW_MINI_GAME_RESULT
    """
    original_caption = pygame.display.get_caption()
    game_id_for_title = gs.current_mini_game_id if gs.current_mini_game_id else "未知游戏"
    pygame.display.set_caption(f"小游戏: {game_id_for_title}")

    game_result = {"message": f"小游戏 '{game_id_for_title}' 未实现或配置错误。", "effect": 0}

    if gs.current_mini_game_id == "reaction_test": # Ensure this ID matches your locations_list.txt
        game_result = mini_game_reaction.play(screen, ai_settings, current_player)
    # elif gs.current_mini_game_id == "memory_cards":
    #     game_result = mini_game_memory_cards.play(screen, ai_settings, current_player)
    # # Add other mini-games here
    else:
        print(f"Warning: Attempted to run unknown or unhandled minigame ID '{gs.current_mini_game_id}'")
        # Fallback message already set in game_result init

    gs.mini_game_result_message = game_result["message"]
    gs.mini_game_player_effect = game_result["effect"] # Store the effect

    # Apply the effect to the player
    if isinstance(gs.mini_game_player_effect, (int, float)):
        current_player.invest(gs.mini_game_player_effect)
    else:
        print(f"Warning: Minigame effect '{gs.mini_game_player_effect}' is not a number.")


    pygame.display.set_caption(original_caption[0])
    gs.game_state = ai_settings.SHOW_MINI_GAME_RESULT

def create_player_queue(ai_settings, screen, locations, pq):
    # 创建所有玩家
    player1 = Player(ai_settings, screen, locations, 1, "曾致元")
    player2 = Player(ai_settings, screen, locations, 2, "孙镜涛")
    player3 = Player(ai_settings, screen, locations, 3, "鞠丰禧")
    # 将所有玩家加入游戏队列
    pq.add_player(player1)
    pq.add_player(player2)
    pq.add_player(player3)