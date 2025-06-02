import pygame
import sys
from player import Qubit
from tools import StealCard,UnlimitedMeasurementCard,Item
from gate import *
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

    def deal_pocession(player, item):
        if item.char==1:
            if item.name == "X门":
                player.add_gate(XGate())
            elif item.name == "Z门":
                player.add_gate(ZGate())
            elif item.name == "H门":
                player.add_gate(HGate())

        elif item.char == 2:
            if item.name == "抢夺卡":
                player.add_item(StealCard())
            elif item.name == "测量卡":
                player.add_item(UnlimitedMeasurementCard())

            else:
                player.add_item(Item())

        elif item.char == 3:
            if item.name == "量子位0":
                player.add_qubit(Qubit(alpha=1,beta=0))
            elif item.name == "量子位1":
                player.add_qubit(Qubit(alpha=0,beta=1))
            elif item.name == "正向量子位":
                player.add_qubit(Qubit(alpha=1, beta=1))
            elif item.name == "负向量子位":
                player.add_qubit(Qubit(alpha=1, beta=1))
           




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
            pygame.image.load("images/card_qubit_pos.png").convert_alpha(),
            pygame.image.load("images/card_qubit_neg.png").convert_alpha(),
            pygame.image.load("images/card_qubit_0.png").convert_alpha(),
            pygame.image.load("images/card_qubit_1.png").convert_alpha(),
            
        ]
        button_image = pygame.image.load("images/button_Buy.png").convert_alpha()
        button_image = pygame.transform.scale(button_image, (200, 80))  # 缩放按钮图片到合适大小

        btn_return_image=pygame.image.load("images/button_return.png").convert_alpha()
        btn_return_image = pygame.transform.scale(btn_return_image, (100, 80))  # 缩放按钮图片到合适大小
        
        # 缩放商品图片到合适大小
        item_images = [pygame.transform.scale(img, (100, 100)) for img in item_images]
        
    except pygame.error as e:
        print(f"无法加载图片: {e}")
        sys.exit()

    # 商品类

    # 返回键
    class ReturnButton:
        def __init__(self, image, x, y):
            self.image = image
            self.rect = self.image.get_rect(topleft=(x, y))
            # self.hovered = False
        
        def draw(self, surface):
            surface.blit(self.image, self.rect)
            
            # 悬停效果
            # if self.hovered:
            #     s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            #     s.fill((255, 255, 255, 50))
            #     surface.blit(s, self.rect)
        
        # def check_hover(self, pos):
        #     self.hovered = self.rect.collidepoint(pos)
        #     return self.hovered
        
        def is_clicked(self, pos, event):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.rect.collidepoint(pos)
            return False

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
        def __init__(self, image, x, y, price, name,char):
            self.image = image
            self.rect = self.image.get_rect(topleft=(x, y))
            self.price = price
            self.name = name
            self.hovered = False
            self.selected = False  # 新增选中状态
            self.char=char
        
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
    return_button = ReturnButton(btn_return_image, 180, 800)
    # 创建商品列表
    items = [
        ShopItem(item_images[0], 170, 230, 200, "X门",1),
        ShopItem(item_images[1], 370, 230, 200, "Z门",1),
        ShopItem(item_images[2], 550, 230, 200, "H门",1),
        ShopItem(item_images[3], 136, 410, 250, "测量卡",2),
        ShopItem(item_images[4], 292, 410, 250, "抢夺卡",2),
        ShopItem(item_images[5], 130, 570, 520, "正向量子位",3),
        ShopItem(item_images[6], 280, 570, 520, "负向量子位",3),
        ShopItem(item_images[7], 440, 570, 320, "量子位0",3),
        ShopItem(item_images[8], 600, 570, 320, "量子位1",3),
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
    purchased_items = []  # 用于记录购买的商品
    total_cost = 0        # 记录总花费
    
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
                    purchased_items.append(selected_item)  # 记录购买的商品
                    total_cost += selected_item.price     # 累加总花
                    deal_pocession(current_player,selected_item)
                    # 购买后取消选中,LC:这里暂时只能买一个
                    selected_item.selected = False
                    selected_item = None
                    # finished=True
                else:
                    print("金币不足!")

            if return_button.is_clicked(mouse_pos, event):
                finished=True
        
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
        
        return_button.draw(screen)
        
        # 显示玩家金币
        gold_text = font.render(f"金币: ${player_gold}", True, BLACK)
        screen.blit(gold_text, (20, 20))
        
        # 显示购买提示
        if selected_item:
            hint_text = font.render(f"已选择: {selected_item.name}", True, BLACK)
            screen.blit(hint_text, (20, 60))

        # 显示已购商品列表
        if purchased_items:
            purchased_text = font.render("已购: " + ", ".join([item.name for item in purchased_items]), True, BLACK)
            screen.blit(purchased_text, (20, 100))

        
        pygame.display.flip()
        clock.tick(60)

        if finished:
            running= False

    pygame.display.set_mode(main_size)
    pygame.display.set_caption(main_caption)

    if purchased_items:
        message = "已购买：" + "、".join([item.name for item in purchased_items]) + f"，总花费：{total_cost}"
    else:
        message = "未购买任何物品"


    return {
    "message": message,
    "cost": total_cost,
    "items": [item.name for item in purchased_items]  # 返回购买的商品列表
}
    
        
        