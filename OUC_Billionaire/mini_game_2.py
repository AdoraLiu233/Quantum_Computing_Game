import numpy as np
import pygame
import random
from pygame.locals import *



def play(screen, gs, ai_settings):
    main_size = screen.get_size()
    main_caption = pygame.display.get_caption()[0]    
    
    # 初始化 Pygame
    pygame.init()
    WIDTH, HEIGHT = 1200, 1000  # 保持原有分辨率不变
    GRID_SIZE = 16
    CELL_SIZE = 50  # 稍微减小单元格大小以适应左边布局
    BOARD_WIDTH = GRID_SIZE * CELL_SIZE
    BOARD_HEIGHT = GRID_SIZE * CELL_SIZE
    RIGHT_PANEL_WIDTH = WIDTH - BOARD_WIDTH - 20  # 右边面板宽度
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Quantum Maze (Grover's Algorithm)")

    # 颜色定义（保持不变）
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    GRAY = (100, 100, 100)  # 障碍墙颜色
    ORACLE_COLOR = (100, 200, 100)
    DIFFUSION_COLOR = (200, 200, 100)
    CHECK_COLOR = (200, 100, 100)
    EXIT_COLOR = (150, 150, 150)
    BUTTON_COLOR = (200, 200, 200)
    PANEL_COLOR = (240, 240, 240)  # 右边面板背景色

    # 字体定义（保持不变）
    try:
        button_font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 24)
        hint_font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 20)
        status_font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 28)
        title_font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 32)
    except:
        button_font = pygame.font.SysFont(None, 24)
        hint_font = pygame.font.SysFont(None, 20)
        status_font = pygame.font.SysFont(None, 28)
        title_font = pygame.font.SysFont(None, 32)

    # 初始化量子态（保持不变）
    probs = np.ones((GRID_SIZE, GRID_SIZE)) / (GRID_SIZE ** 2)
    player_pos = [0, 0]
    
    # 定义迷宫障碍墙（保持不变）
    maze = np.zeros((GRID_SIZE, GRID_SIZE))
    for i in range(GRID_SIZE):
        maze[i][5] = 1 if i not in [2, 3, 7, 8, 12] else 0
        maze[i][10] = 1 if i not in [1, 6, 11, 14] else 0
    for j in range(GRID_SIZE):
        maze[3][j] = 1 if j not in [0, 4, 9, 15] else 0
        maze[12][j] = 1 if j not in [2, 7, 11] else 0
    
    # 确保起点和终点不在墙上（保持不变）
    while True:
        target_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]
        if maze[target_pos[0]][target_pos[1]] == 0 and target_pos != [0, 0]:
            break

    # 操作反馈变量（保持不变）
    action_text = ""
    show_action_text = False
    action_text_time = 0
    ACTION_DISPLAY_TIME = 1000
    show_target = False

    # 提示信息（保持不变）
    show_rules = True
    show_strategy = False
    rules_text = "游戏规则：使用WASD移动，点击按钮应用量子操作寻找目标位置"
    strategy_text = "策略提示：交替使用Oracle和Diffusion操作来放大目标概率"

    # 重新定义按钮位置 - 现在放在右边面板
    button_height = 50
    button_width = RIGHT_PANEL_WIDTH - 40
    button_start_y = 300  # 按钮开始的位置
    
    oracle_button = pygame.Rect(BOARD_WIDTH + 20, button_start_y, button_width, button_height)
    diffusion_button = pygame.Rect(BOARD_WIDTH + 20, button_start_y + 70, button_width, button_height)
    check_button = pygame.Rect(BOARD_WIDTH + 20, button_start_y + 140, button_width, button_height)
    exit_button = pygame.Rect(BOARD_WIDTH + 20, button_start_y + 210, button_width, button_height)

    # Grover 操作（保持不变）
    def grover_oracle(amplitudes, target):
        new_amp = amplitudes.copy()
        new_amp[target[0]][target[1]] *= -1
        return new_amp

    def diffusion_operator(amplitudes):
        mean_amplitude = np.mean(amplitudes)
        amplitudes = (2 * mean_amplitude) - amplitudes
        amplitudes=amplitudes / np.linalg.norm(amplitudes)
        return amplitudes

    def get_hint(player_pos, amplitudes):
        probabilities = np.abs(amplitudes) ** 2
        max_prob_pos = np.unravel_index(np.argmax(probabilities), probabilities.shape)

        dr = max_prob_pos[0] - player_pos[0]
        dc = max_prob_pos[1] - player_pos[1]
        
        if abs(dr) > abs(dc):
            return "up" if dr < 0 else "down"
        else:
            return "left" if dc < 0 else "right"

    # 游戏主循环
    running = True
    hint_text = ""
    game_status = "Playing"

    while running:
        screen.fill(WHITE)
        
        # 绘制右边面板背景
        pygame.draw.rect(screen, PANEL_COLOR, (BOARD_WIDTH, 0, RIGHT_PANEL_WIDTH, HEIGHT))
        
        # 检查操作反馈是否超时
        current_time = pygame.time.get_ticks()
        if show_action_text and (current_time - action_text_time > ACTION_DISPLAY_TIME):
            show_action_text = False
        
        # 绘制棋盘
        board_start_x = 20
        board_start_y = (HEIGHT - BOARD_HEIGHT) // 2  # 垂直居中
        
        # 绘制网格和障碍墙
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(board_start_x + c * CELL_SIZE, board_start_y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, BLACK, rect, 1)
                if maze[r][c] == 1:  # 绘制障碍墙
                    pygame.draw.rect(screen, GRAY, rect)
        
        # 绘制玩家（蓝色）
        pygame.draw.rect(
            screen, BLUE,
            (board_start_x + player_pos[1] * CELL_SIZE, board_start_y + player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )
        
        # 如果游戏结束或点击了Check按钮，显示目标位置
        if show_target or game_status != "Playing":
            pygame.draw.rect(
                screen, RED,
                (board_start_x + target_pos[1] * CELL_SIZE, board_start_y + target_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )
        
        # 绘制右边面板内容
        # 1. 游戏标题
        title_surface = title_font.render("量子迷宫", True, BLACK)
        screen.blit(title_surface, (BOARD_WIDTH + (RIGHT_PANEL_WIDTH - title_surface.get_width()) // 2, 30))
        
        # 2. 规则和策略提示
        rules_button = pygame.Rect(BOARD_WIDTH + 20, 100, RIGHT_PANEL_WIDTH - 40, 30)
        strategy_button = pygame.Rect(BOARD_WIDTH + 20, 140, RIGHT_PANEL_WIDTH - 40, 30)
        
        pygame.draw.rect(screen, BUTTON_COLOR, rules_button)
        pygame.draw.rect(screen, BUTTON_COLOR, strategy_button)
        
        rules_btn_text = button_font.render("游戏规则", True, BLACK)
        strategy_btn_text = button_font.render("策略查询", True, BLACK)
        
        screen.blit(rules_btn_text, (rules_button.x + (rules_button.width - rules_btn_text.get_width()) // 2, 
                                    rules_button.y + (rules_button.height - rules_btn_text.get_height()) // 2))
        screen.blit(strategy_btn_text, (strategy_button.x + (strategy_button.width - strategy_btn_text.get_width()) // 2, 
                                      strategy_button.y + (strategy_button.height - strategy_btn_text.get_height()) // 2))
        
        # 显示提示信息
        if show_rules:
            rules_lines = [rules_text[i:i+30] for i in range(0, len(rules_text), 30)]
            for i, line in enumerate(rules_lines):
                rules_surface = hint_font.render(line, True, BLACK)
                screen.blit(rules_surface, (BOARD_WIDTH + 20, 180 + i * 25))
        
        if show_strategy:
            strategy_lines = [strategy_text[i:i+30] for i in range(0, len(strategy_text), 30)]
            for i, line in enumerate(strategy_lines):
                strategy_surface = hint_font.render(line, True, BLACK)
                screen.blit(strategy_surface, (BOARD_WIDTH + 20, 180 + i * 25))
        
        # 3. 绘制操作按钮
        pygame.draw.rect(screen, ORACLE_COLOR, oracle_button)
        pygame.draw.rect(screen, DIFFUSION_COLOR, diffusion_button)
        pygame.draw.rect(screen, CHECK_COLOR, check_button)
        pygame.draw.rect(screen, EXIT_COLOR, exit_button)
        
        # 按钮文字
        oracle_text = button_font.render("Oracle", True, BLACK)
        diffusion_text = button_font.render("Diffusion", True, BLACK)
        check_text = button_font.render("Check", True, BLACK)
        exit_text = button_font.render("Exit", True, BLACK)
        
        # 居中按钮文字
        screen.blit(oracle_text, (oracle_button.x + (button_width - oracle_text.get_width()) // 2, 
                                oracle_button.y + (button_height - oracle_text.get_height()) // 2))
        screen.blit(diffusion_text, (diffusion_button.x + (button_width - diffusion_text.get_width()) // 2, 
                                    diffusion_button.y + (button_height - diffusion_text.get_height()) // 2))
        screen.blit(check_text, (check_button.x + (button_width - check_text.get_width()) // 2, 
                                check_button.y + (button_height - check_text.get_height()) // 2))
        screen.blit(exit_text, (exit_button.x + (button_width - exit_text.get_width()) // 2, 
                                exit_button.y + (button_height - exit_text.get_height()) // 2))
        
        # 4. 显示操作反馈
        if show_action_text:
            action_surface = hint_font.render(action_text, True, BLACK)
            screen.blit(action_surface, (BOARD_WIDTH + 20, button_start_y + 280))
        
        # 5. 显示游戏状态
        if game_status == "Win":
            result_surface = status_font.render("恭喜！你找到了目标！", True, GREEN)
        elif game_status == "Lose":
            result_surface = status_font.render("游戏失败！", True, RED)
        else:
            result_surface = status_font.render("游戏中...", True, BLACK)
        screen.blit(result_surface, (BOARD_WIDTH + 20, button_start_y + 320))
        
        # 6. 显示当前提示
        if hint_text:
            hint_surface = hint_font.render(f"提示: 向 {hint_text} 方向移动", True, BLACK)
            screen.blit(hint_surface, (BOARD_WIDTH + 20, button_start_y + 360))
        
        pygame.display.flip()
        
        # 事件处理（保持不变）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 检查是否点击规则/策略按钮
                if rules_button.collidepoint(mouse_pos):
                    show_rules = not show_rules
                    show_strategy = False
                elif strategy_button.collidepoint(mouse_pos):
                    show_strategy = not show_strategy
                    show_rules = False
                
                # 检查是否点击Exit按钮
                elif exit_button.collidepoint(mouse_pos):
                    if game_status == "Win":
                        pygame.display.set_mode(main_size)
                        pygame.display.set_caption(main_caption)
                        return {
                            "message": "量子迷宫挑战成功！找到了目标！获得资金100元",
                            "effect": 100
                        }
                    elif game_status == "Lose":
                        pygame.display.set_mode(main_size)
                        pygame.display.set_caption(main_caption)
                        return {
                            "message": "量子迷宫挑战失败，但获得了经验。获得资金10元",
                            "effect": 10
                        }
                    else:
                        pygame.display.set_mode(main_size)
                        pygame.display.set_caption(main_caption)
                        return {
                            "message": "量子迷宫游戏退出。未获得资金",
                            "effect": 0
                        }
                
                # 游戏进行中时的按钮处理
                elif game_status == "Playing":
                    if oracle_button.collidepoint(mouse_pos):
                        probs = grover_oracle(probs, target_pos)
                        action_text = "执行Oracle操作！"
                        show_action_text = True
                        action_text_time = pygame.time.get_ticks()
                        hint_text = get_hint(player_pos, probs)
                    
                    elif diffusion_button.collidepoint(mouse_pos):
                        probs = diffusion_operator(probs)
                        action_text = "执行Diffusion操作！"
                        show_action_text = True
                        action_text_time = pygame.time.get_ticks()
                        hint_text = get_hint(player_pos, probs)
                    
                    elif check_button.collidepoint(mouse_pos):
                        show_target = True
                        if player_pos == target_pos:
                            game_status = "Win"
                        else:
                            game_status = "Lose"
            
            # 玩家移动控制（保持不变）
            if game_status == "Playing" and event.type == pygame.KEYDOWN:
                new_pos = player_pos.copy()
                
                if event.key == pygame.K_w and player_pos[0] > 0:
                    new_pos[0] -= 1
                elif event.key == pygame.K_s and player_pos[0] < GRID_SIZE - 1:
                    new_pos[0] += 1
                elif event.key == pygame.K_a and player_pos[1] > 0:
                    new_pos[1] -= 1
                elif event.key == pygame.K_d and player_pos[1] < GRID_SIZE - 1:
                    new_pos[1] += 1
                
                if maze[new_pos[0]][new_pos[1]] == 0:
                    player_pos = new_pos
                    hint_text = ""