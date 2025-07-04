# -*- coding: utf-8 -*-
import pygame

class Settings():
    """初始化游戏设置"""
    def __init__(self):
        # 设置屏幕的大小和颜色
        self.screen_width = 1200
        self.screen_height = 1000  #660
        self.screen_size = (self.screen_width, self.screen_height)
        self.bg_color = (230, 230, 230)
        self.max_rounds = 8 # 最大游戏轮数
        
        # 设置游戏统计信息
        self.ROLL_DICE = 0
        self.CHOOSE = 1
        self.END_ROUND = 2
        self.MINI_GAME_STARTING = 3 # 准备进入小游戏
        self.MINI_GAME_ACTIVE = 4   # 小游戏正在进行
        self.SHOW_MINI_GAME_RESULT = 5 # 显示小游戏结果

        self.SHOP_ACTIVE = 6 # 商店状态
        self.SHOP_ENTERING =10 # 进入商店状态
        self.SHOP_RESULT=11 # 商店结果状态

       
        self.GAME_OVER = 9
        self.GET_QUBIT=7 # 获得qubit
        self.GET_ITEM=8 # 获得道具

        self.SHOW_INVENTORY = 12

        # 用于从其他模块安全访问地点实例列表 (例如传送功能)
        self.locations_instance_list = []

        # 小游戏列表
        self.minigame_configs={
            "mini_game_2": {"name": "liuliu的小游戏"},
            "quantum_bomb": {"name": "量子炸弹"},
            "simon": {"name": "众里寻s千百度"},
        }
        
        # 设置游戏开始前的背景图片
        self.bg_image = pygame.image.load("images/enter.png")
        # 设置开始游戏按钮
        self.play_button = pygame.image.load("images/play_button.png")
        
        # 设置清华地图
        self.map = pygame.image.load("images/map.png")

        #设置商店图片
        self.shop_image = pygame.image.load("images/shop.png")

        # 设置背包背景
        self.backpack_image = pygame.transform.scale(
            pygame.image.load("images/backpack.jpeg"),
            (self.screen_width, self.screen_height)
        )

        # 设置获得qubit/道具时图片
        self.get_qubit_item_image = pygame.image.load("images/get_qubit_item.png")
        # 奖励信息字体设置
        self.reward_font_large = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 32)
        self.reward_font_small = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 24)
        self.reward_text_color = (0, 0, 0)
        self.reward_bg_color = (255, 255, 255, 200)  # 半透明白色
        
        # 设置玩家初始拥有的金钱
        self.player_init_money = 1000
        
        # 设置地点圆点半径大小和颜色
        self.circle_radius = 6
        self.circle_color = (0, 0, 0)
        
        # 设置地点之间连线的颜色
        self.line_color = (0, 0, 0)
        
        # 设置信息面板背景颜色
        self.board_color_1 = (187, 255, 255)
        self.board_color_2 = (255, 250, 205)
        self.board_color_3 = (255, 218, 185)
        
        # 设置地图上地点数量
        self.location_cnt = 0
        
        # 设置地点事件数量
        self.event_cnt = 0
        
        # 设置地点数据文件路径
        self.locations_data_path = "data/locations_list.txt"
        
        # 设置地点事件文件路径
        self.events_path = "data/events_list.json"
        
        # 设置地点事件图片路径
        self.event_images_dir = "event_images"
        