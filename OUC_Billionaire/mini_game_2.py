import numpy as np
import pygame
import random
from pygame.locals import *

# 初始化 Pygame
pygame.init()
WIDTH, HEIGHT = 800, 850  # 增加 50px 给按钮
GRID_SIZE = 16
CELL_SIZE = WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Maze (Grover's Algorithm)")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORACLE_COLOR = (100, 200, 100)  # 深绿色
DIFFUSION_COLOR = (200, 200, 100)  # 深黄色
CHECK_COLOR = (200, 100, 100)  # 深红色

# 初始化量子态（16×16 网格，均匀分布）
probs = np.ones((GRID_SIZE, GRID_SIZE)) / (GRID_SIZE ** 2)
player_pos = [0, 0]  # 玩家初始位置 (0, 0)
target_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]  # 随机终点

# 操作反馈变量
action_text = ""
show_action_text = False
action_text_time = 0
ACTION_DISPLAY_TIME = 1000  # 显示操作反馈的时间（毫秒）

# Grover 操作
def grover_oracle(probs, target):
    """Oracle: 标记终点（翻转相位）"""
    new_probs = probs.copy()
    new_probs[target[0], target[1]] *= -1  # 相位翻转（量子态操作）
    return new_probs

def diffusion_operator(probs):
    """Diffusion: 绕均值反转"""
    mean = np.mean(probs)
    new_probs = 2 * mean - probs  # 绕均值反转
    return new_probs / np.sum(new_probs)  # 归一化

def get_hint(player_pos, probs):
    """返回最大概率格子的方向提示（如 'up', 'right'）"""
    max_prob_pos = np.unravel_index(np.argmax(probs), probs.shape)
    dr = max_prob_pos[0] - player_pos[0]
    dc = max_prob_pos[1] - player_pos[1]
    
    if abs(dr) > abs(dc):
        return "up" if dr < 0 else "down"
    else:
        return "left" if dc < 0 else "right"

# 按钮定义
button_height = 50
oracle_button = pygame.Rect(0, HEIGHT - button_height, WIDTH // 3, button_height)
diffusion_button = pygame.Rect(WIDTH // 3, HEIGHT - button_height, WIDTH // 3, button_height)
check_button = pygame.Rect(2 * WIDTH // 3, HEIGHT - button_height, WIDTH // 3, button_height)

# 游戏主循环
running = True
font = pygame.font.SysFont(None, 36)
hint_text = ""
game_status = "Playing"  # "Playing", "Win", "Lose"

while running:
    screen.fill(WHITE)
    
    # 检查操作反馈是否超时
    current_time = pygame.time.get_ticks()
    if show_action_text and (current_time - action_text_time > ACTION_DISPLAY_TIME):
        show_action_text = False
    
    # 绘制网格
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)
    
    # 绘制玩家（蓝色）
    pygame.draw.rect(
        screen, BLUE,
        (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )
    
    # 绘制终点（红色，但玩家不可见）
    if game_status != "Playing":
        pygame.draw.rect(
            screen, RED,
            (target_pos[1] * CELL_SIZE, target_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )
    
    # 绘制按钮
    pygame.draw.rect(screen, ORACLE_COLOR, oracle_button)
    pygame.draw.rect(screen, DIFFUSION_COLOR, diffusion_button)
    pygame.draw.rect(screen, CHECK_COLOR, check_button)
    
    # 按钮文字
    oracle_text = font.render("Oracle", True, BLACK)
    diffusion_text = font.render("Diffusion", True, BLACK)
    check_text = font.render("Check", True, BLACK)
    
    screen.blit(oracle_text, (oracle_button.x + 20, oracle_button.y + 15))
    screen.blit(diffusion_text, (diffusion_button.x + 10, diffusion_button.y + 15))
    screen.blit(check_text, (check_button.x + 20, check_button.y + 15))
    
    # 显示提示或操作反馈
    if show_action_text:
        hint_surface = font.render(action_text, True, BLACK)
    else:
        hint_surface = font.render(f"Hint: {hint_text}", True, BLACK)
    screen.blit(hint_surface, (10, 10))
    
    # 显示游戏状态
    if game_status == "Win":
        result_surface = font.render("Congratulations! You found the target!", True, GREEN)
    elif game_status == "Lose":
        result_surface = font.render("You lose! Try again.", True, RED)
    else:
        result_surface = font.render("Playing...", True, BLACK)
    screen.blit(result_surface, (10, 50))
    
    pygame.display.flip()
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        if game_status == "Playing":
            if event.type == KEYDOWN:
                # WASD 移动
                if event.key == K_w and player_pos[0] > 0:
                    player_pos[0] -= 1
                    hint_text = ""  # 移动后提示消失
                elif event.key == K_s and player_pos[0] < GRID_SIZE - 1:
                    player_pos[0] += 1
                    hint_text = ""
                elif event.key == K_a and player_pos[1] > 0:
                    player_pos[1] -= 1
                    hint_text = ""
                elif event.key == K_d and player_pos[1] < GRID_SIZE - 1:
                    player_pos[1] += 1
                    hint_text = ""
            
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 检查点击哪个按钮
                if oracle_button.collidepoint(mouse_pos):
                    probs = grover_oracle(probs, target_pos)
                    action_text = "Click Oracle!"
                    show_action_text = True
                    action_text_time = pygame.time.get_ticks()
                    hint_text = get_hint(player_pos, probs)
                
                elif diffusion_button.collidepoint(mouse_pos):
                    probs = diffusion_operator(probs)
                    action_text = "Click Diffusion!"
                    show_action_text = True
                    action_text_time = pygame.time.get_ticks()
                    hint_text = get_hint(player_pos, probs)
                
                elif check_button.collidepoint(mouse_pos):
                    if player_pos == target_pos:
                        game_status = "Win"
                    else:
                        game_status = "Lose"

pygame.quit()

# import numpy as np
# import pygame
# import random
# from pygame.locals import *

# # 初始化 Pygame
# pygame.init()
# WIDTH, HEIGHT = 800, 850  # 增加 50px 给按钮
# GRID_SIZE = 16
# CELL_SIZE = WIDTH // GRID_SIZE
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Quantum Maze (Grover's Algorithm)")

# # 颜色定义
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# GREEN = (0, 255, 0)
# RED = (255, 0, 0)
# BLUE = (0, 0, 255)
# YELLOW = (255, 255, 0)
# ORACLE_COLOR = (100, 200, 100)  # 深绿色
# DIFFUSION_COLOR = (200, 200, 100)  # 深黄色
# CHECK_COLOR = (200, 100, 100)  # 深红色

# # 初始化量子态（16×16 网格，均匀分布）
# probs = np.ones((GRID_SIZE, GRID_SIZE)) / (GRID_SIZE ** 2)
# player_pos = [0, 0]  # 玩家初始位置 (0, 0)
# target_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]  # 随机终点

# # 操作反馈变量
# action_text = ""
# show_action_text = False
# action_text_time = 0
# ACTION_DISPLAY_TIME = 1000  # 显示操作反馈的时间（毫秒）

# # 字体定义
# font = pygame.font.SysFont(None, 36)
# small_font = pygame.font.SysFont(None, 20)  # 用于显示概率的小字体

# # Grover 操作
# def grover_oracle(probs, target):
#     """Oracle: 标记终点（翻转相位）"""
#     new_probs = probs.copy()
#     new_probs[target[0], target[1]] *= -1  # 相位翻转（量子态操作）
#     return new_probs

# def diffusion_operator(probs):
#     """Diffusion: 绕均值反转"""
#     mean = np.mean(probs)
#     new_probs = 2 * mean - probs  # 绕均值反转
#     return new_probs / np.sum(new_probs)  # 归一化

# def get_hint(player_pos, probs):
#     """返回最大概率格子的方向提示（如 'up', 'right'）"""
#     max_prob_pos = np.unravel_index(np.argmax(probs), probs.shape)
#     dr = max_prob_pos[0] - player_pos[0]
#     dc = max_prob_pos[1] - player_pos[1]
    
#     if abs(dr) > abs(dc):
#         return "up" if dr < 0 else "down"
#     else:
#         return "left" if dc < 0 else "right"

# # 按钮定义
# button_height = 50
# oracle_button = pygame.Rect(0, HEIGHT - button_height, WIDTH // 3, button_height)
# diffusion_button = pygame.Rect(WIDTH // 3, HEIGHT - button_height, WIDTH // 3, button_height)
# check_button = pygame.Rect(2 * WIDTH // 3, HEIGHT - button_height, WIDTH // 3, button_height)

# # 游戏主循环
# running = True
# hint_text = ""
# game_status = "Playing"  # "Playing", "Win", "Lose"

# while running:
#     screen.fill(WHITE)
    
#     # 检查操作反馈是否超时
#     current_time = pygame.time.get_ticks()
#     if show_action_text and (current_time - action_text_time > ACTION_DISPLAY_TIME):
#         show_action_text = False
    
#     # 绘制网格和概率
#     for r in range(GRID_SIZE):
#         for c in range(GRID_SIZE):
#             rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
#             pygame.draw.rect(screen, BLACK, rect, 1)
            
#             # 计算并显示概率（概率幅的平方）
#             prob = probs[r, c]**2
#             prob_text = small_font.render(f"{prob:.2f}", True, BLACK)
            
#             # 在格子中心显示概率
#             text_rect = prob_text.get_rect(center=rect.center)
#             screen.blit(prob_text, text_rect)
    
#     # 绘制玩家（蓝色）
#     pygame.draw.rect(
#         screen, BLUE,
#         (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
#     )
    
#     # 绘制终点（红色，但玩家不可见）
#     if game_status != "Playing":
#         pygame.draw.rect(
#             screen, RED,
#             (target_pos[1] * CELL_SIZE, target_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
#         )
    
#     # 绘制按钮
#     pygame.draw.rect(screen, ORACLE_COLOR, oracle_button)
#     pygame.draw.rect(screen, DIFFUSION_COLOR, diffusion_button)
#     pygame.draw.rect(screen, CHECK_COLOR, check_button)
    
#     # 按钮文字
#     oracle_text = font.render("Oracle", True, BLACK)
#     diffusion_text = font.render("Diffusion", True, BLACK)
#     check_text = font.render("Check", True, BLACK)
    
#     screen.blit(oracle_text, (oracle_button.x + 20, oracle_button.y + 15))
#     screen.blit(diffusion_text, (diffusion_button.x + 10, diffusion_button.y + 15))
#     screen.blit(check_text, (check_button.x + 20, check_button.y + 15))
    
#     # 显示提示或操作反馈
#     if show_action_text:
#         hint_surface = font.render(action_text, True, BLACK)
#     else:
#         hint_surface = font.render(f"Hint: {hint_text}", True, BLACK)
#     screen.blit(hint_surface, (10, 10))
    
#     # 显示游戏状态
#     if game_status == "Win":
#         result_surface = font.render("Congratulations! You found the target!", True, GREEN)
#     elif game_status == "Lose":
#         result_surface = font.render("You lose! Try again.", True, RED)
#     else:
#         result_surface = font.render("Playing...", True, BLACK)
#     screen.blit(result_surface, (10, 50))
    
#     pygame.display.flip()
    
#     # 事件处理
#     for event in pygame.event.get():
#         if event.type == QUIT:
#             running = False
        
#         if game_status == "Playing":
#             if event.type == KEYDOWN:
#                 # WASD 移动
#                 if event.key == K_w and player_pos[0] > 0:
#                     player_pos[0] -= 1
#                     hint_text = ""  # 移动后提示消失
#                 elif event.key == K_s and player_pos[0] < GRID_SIZE - 1:
#                     player_pos[0] += 1
#                     hint_text = ""
#                 elif event.key == K_a and player_pos[1] > 0:
#                     player_pos[1] -= 1
#                     hint_text = ""
#                 elif event.key == K_d and player_pos[1] < GRID_SIZE - 1:
#                     player_pos[1] += 1
#                     hint_text = ""
            
#             elif event.type == MOUSEBUTTONDOWN:
#                 mouse_pos = pygame.mouse.get_pos()
                
#                 # 检查点击哪个按钮
#                 if oracle_button.collidepoint(mouse_pos):
#                     probs = grover_oracle(probs, target_pos)
#                     action_text = "Click Oracle!"
#                     show_action_text = True
#                     action_text_time = pygame.time.get_ticks()
#                     hint_text = get_hint(player_pos, probs)
                
#                 elif diffusion_button.collidepoint(mouse_pos):
#                     probs = diffusion_operator(probs)
#                     action_text = "Click Diffusion!"
#                     show_action_text = True
#                     action_text_time = pygame.time.get_ticks()
#                     hint_text = get_hint(player_pos, probs)
                
#                 elif check_button.collidepoint(mouse_pos):
#                     if player_pos == target_pos:
#                         game_status = "Win"
#                     else:
#                         game_status = "Lose"

# pygame.quit()