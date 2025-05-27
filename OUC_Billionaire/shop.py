import pygame
import sys
def play(screen, ai_settings, current_player):
    print("11111111111111")
    global player_gold
    main_size = screen.get_size()
    main_caption = pygame.display.get_caption()[0]    
    # 初始化pygame
    pygame.init()

    # 设置屏幕尺寸
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 1000
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("量子商店")

    # 颜色定义
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    # 加载图片
    try:
        background = pygame.image.load("images/shop.png").convert()
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 假设我们有3种商品
        item_images = [
            pygame.image.load("images/card_X.png").convert_alpha(),
            pygame.image.load("images/card_Z.png").convert_alpha(),
            pygame.image.load("images/card_H.png").convert_alpha(),
            pygame.image.load("images/card_Measure.png").convert_alpha(),
            pygame.image.load("images/card_Grab.png").convert_alpha(),
            pygame.image.load("images/card_Dice.png").convert_alpha(),
            pygame.image.load("images/card_qubit_pos.png").convert_alpha(),
            pygame.image.load("images/card_qubit_neg.png").convert_alpha(),
            pygame.image.load("images/card_qubit_0.png").convert_alpha(),
            pygame.image.load("images/card_qubit_1.png").convert_alpha(),
        ]
        button_image = pygame.image.load("images/button_Buy.png").convert_alpha()
        button_image = pygame.transform.scale(button_image, (200, 80))  # 缩放按钮图片到合适大小
        
        # 缩放商品图片到合适大小
        item_images = [pygame.transform.scale(img, (100, 100)) for img in item_images]
        
    except pygame.error as e:
        print(f"无法加载图片: {e}")
        sys.exit()

    # 商品类

    # 购买按钮类
    class BuyButton:
        def __init__(self, image, x, y):
            self.image = image
            self.rect = self.image.get_rect(topleft=(x, y))
            self.hovered = False
        
        def draw(self, surface):
            surface.blit(self.image, self.rect)
            
            # 悬停效果
            if self.hovered:
                s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                s.fill((255, 255, 255, 50))
                surface.blit(s, self.rect)
        
        def check_hover(self, pos):
            self.hovered = self.rect.collidepoint(pos)
            return self.hovered
        
        def is_clicked(self, pos, event):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.rect.collidepoint(pos)
            return False
    # 商品类
    class ShopItem:
        def __init__(self, image, x, y, price, name):
            self.image = image
            self.rect = self.image.get_rect(topleft=(x, y))
            self.price = price
            self.name = name
            self.hovered = False
            self.selected = False  # 新增选中状态
        
        def draw(self, surface):
            surface.blit(self.image, self.rect)
            
            # 如果选中商品，绘制选中框
            if self.selected:
                pygame.draw.rect(surface, GREEN, self.rect, 2)
            
            # 显示商品信息
            if self.hovered or self.selected:
                font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 24)
                name_text = font.render(f"{self.name}", True, BLACK)
                price_text = font.render(f"价格: ${self.price}", True, RED)
                
                info_rect = pygame.Rect(self.rect.x, self.rect.bottom + 5, 
                                    max(name_text.get_width(), price_text.get_width()),
                                    name_text.get_height() + price_text.get_height())
                
                s = pygame.Surface((info_rect.width, info_rect.height), pygame.SRCALPHA)
                s.fill((255, 255, 255, 200))
                surface.blit(s, info_rect)
                
                surface.blit(name_text, (self.rect.x, self.rect.bottom + 5))
                surface.blit(price_text, (self.rect.x, self.rect.bottom + 5 + name_text.get_height()))
        
        def check_hover(self, pos):
            self.hovered = self.rect.collidepoint(pos)
            return self.hovered
        
        def check_click(self, pos, event):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(pos):
                    self.selected = True
                    return True
            return False



    #创建购买按钮
    buy_button = BuyButton(button_image, 415, 800)
    # 创建商品列表
    items = [
        ShopItem(item_images[0], 170, 230, 100, "X门"),
        ShopItem(item_images[1], 370, 230, 200, "Z门"),
        ShopItem(item_images[2], 550, 230, 300, "H门"),
        ShopItem(item_images[3], 136, 410, 150, "测量卡"),
        ShopItem(item_images[4], 292, 410, 250, "抢夺卡"),
        ShopItem(item_images[5], 447, 410, 350, "神奇骰子"),
        ShopItem(item_images[6], 130, 570, 120, "正向量子位"),
        ShopItem(item_images[7], 280, 570, 120, "负向量子位"),
        ShopItem(item_images[8], 440, 570, 150, "量子位0"),
        ShopItem(item_images[9], 600, 570, 150, "量子位1"),
    ]

    # 玩家金币
    player_gold = current_player.money

    # 字体
    font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 24)

    # 游戏主循环
    # 游戏主循环

    
    
    
    clock = pygame.time.Clock()
    running = True
    selected_item = None  # 当前选中的商品
    finished=False
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 检测商品点击
            for item in items:
                if item.check_click(mouse_pos, event):
                    # 取消之前选中的商品
                    if selected_item:
                        selected_item.selected = False
                    # 选中当前商品
                    selected_item = item
                    item.selected = True
            
            # 检测购买按钮点击
            if buy_button.is_clicked(mouse_pos, event) and selected_item:
                if player_gold >= selected_item.price:
                    player_gold -= selected_item.price
                    print(f"购买了 {selected_item.name}!")
                    # 购买后取消选中,LC:这里暂时只能买一个
                    selected_item.selected = False
                    # selected_item = None
                    finished=True
                else:
                    print("金币不足!")
        
        # 更新悬停状态
        for item in items:
            item.check_hover(mouse_pos)
        buy_button.check_hover(mouse_pos)
        
        # 绘制背景
        screen.blit(background, (0, 0))
        
        # 绘制商品
        for item in items:
            item.draw(screen)
        
        # 绘制购买按钮（如果已选中商品）
        if selected_item:
            buy_button.draw(screen)
        
        # 显示玩家金币
        gold_text = font.render(f"金币: ${player_gold}", True, BLACK)
        screen.blit(gold_text, (20, 20))
        
        # 显示购买提示
        if selected_item:
            hint_text = font.render(f"已选择: {selected_item.name}", True, BLACK)
            screen.blit(hint_text, (20, 60))
        
        pygame.display.flip()
        clock.tick(60)

        if finished:
            running= False

    pygame.display.set_mode(main_size)
    pygame.display.set_caption(main_caption)
    return {
        "message": "已购买："+ selected_item.name,
        "cost": selected_item.price,
    }
    
        
        # pygame.quit()
        # sys.exit()

# if __name__ == "__main__":
#     play()

# class Shop:
#     def __init__(self, screen_width, screen_height):
#         self.screen_width = screen_width
#         self.screen_height = screen_height
        
#         # 颜色定义
#         self.WHITE = (255, 255, 255)
#         self.BLACK = (0, 0, 0)
#         self.GREEN = (0, 255, 0)
#         self.RED = (255, 0, 0)
        
#         # 加载资源
#         self.load_resources()
        
#         # 初始化商店物品和按钮
#         self.initialize_shop()
        
#         # 当前选中的商品
#         self.selected_item = None
        
#         # 字体
#         self.font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 24)
    
#     def load_resources(self):
#         """加载所有商店需要的资源"""
#         try:
#             self.background = pygame.image.load("images/shop.png").convert()
#             self.background = pygame.transform.scale(
#                 self.background, (self.screen_width, self.screen_height))
            
#             # 加载商品图片
#             item_paths = [
#                 "images/card_X.png", "images/card_Z.png", "images/card_H.png",
#                 "images/card_Measure.png", "images/card_Grab.png",
#                 "images/card_Dice.png", "images/card_qubit_pos.png",
#                 "images/card_qubit_neg.png", "images/card_qubit_0.png",
#                 "images/card_qubit_1.png"
#             ]
            
#             self.item_images = [
#                 pygame.transform.scale(
#                     pygame.image.load(path).convert_alpha(), 
#                     (100, 100)
#                 ) for path in item_paths
#             ]
            
#             # 加载按钮图片
#             self.button_image = pygame.transform.scale(
#                 pygame.image.load("images/button_Buy.png").convert_alpha(),
#                 (200, 80)
#             )
                
#         except pygame.error as e:
#             print(f"无法加载商店资源: {e}")
#             raise
    
#     def initialize_shop(self):
#         """初始化商店物品和按钮"""
#         # 创建商品列表
#         self.items = [
#             ShopItem(self.item_images[0], 170, 230, 100, "X门"),
#             ShopItem(self.item_images[1], 370, 230, 200, "Z门"),
#             ShopItem(self.item_images[2], 550, 230, 300, "H门"),
#             ShopItem(self.item_images[3], 136, 410, 150, "测量卡"),
#             ShopItem(self.item_images[4], 292, 410, 250, "抢夺卡"),
#             ShopItem(self.item_images[5], 447, 410, 350, "神奇骰子"),
#             ShopItem(self.item_images[6], 130, 570, 120, "正向量子位"),
#             ShopItem(self.item_images[7], 280, 570, 120, "负向量子位"),
#             ShopItem(self.item_images[8], 440, 570, 150, "量子位0"),
#             ShopItem(self.item_images[9], 600, 570, 150, "量子位1"),
#         ]
        
#         # 创建购买按钮
#         self.buy_button = BuyButton(self.button_image, 415, 800)
    
#     def handle_events(self, event, mouse_pos, player_gold):
#         """处理商店界面的事件"""
#         # 检测商品点击
#         for item in self.items:
#             if item.check_click(mouse_pos, event):
#                 # 取消之前选中的商品
#                 if self.selected_item:
#                     self.selected_item.selected = False
#                 # 选中当前商品
#                 self.selected_item = item
#                 item.selected = True
        
#         # 检测购买按钮点击
#         if (self.buy_button.is_clicked(mouse_pos, event) and 
#             self.selected_item):
#             if player_gold >= self.selected_item.price:
#                 player_gold -= self.selected_item.price
#                 print(f"购买了 {self.selected_item.name}!")
#                 # 购买后取消选中
#                 self.selected_item.selected = False
#                 purchased_item = self.selected_item
#                 self.selected_item = None
#                 return player_gold, purchased_item
#             else:
#                 print("金币不足!")
        
#         return player_gold, None
    
#     def update(self, mouse_pos):
#         """更新悬停状态"""
#         for item in self.items:
#             item.check_hover(mouse_pos)
#         self.buy_button.check_hover(mouse_pos)
    
#     def draw(self, screen, player_gold):
#         """绘制商店界面"""
#         # 绘制背景
#         screen.blit(self.background, (0, 0))
        
#         # 绘制商品
#         for item in self.items:
#             item.draw(screen)
        
#         # 绘制购买按钮（如果已选中商品）
#         if self.selected_item:
#             self.buy_button.draw(screen)
        
#         # 显示玩家金币
#         gold_text = self.font.render(f"金币: ${player_gold}", True, self.BLACK)
#         screen.blit(gold_text, (20, 20))
        
#         # 显示购买提示
#         if self.selected_item:
#             hint_text = self.font.render(
#                 f"已选择: {self.selected_item.name}", True, self.BLACK)
#             screen.blit(hint_text, (20, 60))
