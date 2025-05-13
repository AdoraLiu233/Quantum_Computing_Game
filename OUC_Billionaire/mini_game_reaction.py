import pygame
import random
import sys # For Quit

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game parameters
SHAPE_WIDTH = 150
SHAPE_HEIGHT = 150
TARGET_COLOR = GREEN
OTHER_COLORS = [RED, BLUE, YELLOW, (128, 0, 128)] # Purple
COLOR_CHANGE_INTERVAL = 500  # milliseconds (how often color changes)
GREEN_DISPLAY_TIME = 1500   # milliseconds (how long green stays before timeout)

def play(screen, ai_settings, current_player):
    """
    Runs the Reaction Test mini-game.

    Args:
        screen: The main Pygame screen surface.
        ai_settings: The game's settings object.
        current_player: The player object (for potential future use, e.g., name display).

    Returns:
        A dictionary containing:
            "message": str (result message, e.g., "Reaction Test: Victory!")
            "effect": int (e.g., money change for the player)
    """
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    shape_rect = pygame.Rect(
        (screen_width - SHAPE_WIDTH) // 2,
        (screen_height - SHAPE_HEIGHT) // 2,
        SHAPE_WIDTH,
        SHAPE_HEIGHT
    )
    current_shape_color = random.choice(OTHER_COLORS)

    font_large = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 48)
    font_small = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 24)

    instruction_text = font_small.render("当方块变绿时，快速点击它!", True, BLACK)
    instruction_rect = instruction_text.get_rect(center=(screen_width // 2, shape_rect.top - 50))

    result_text_surface = None
    game_over = False
    player_won = False

    last_color_change_time = pygame.time.get_ticks()
    is_target_color_active = False
    target_color_start_time = 0

    mini_game_running = True
    game_clock = pygame.time.Clock()

    while mini_game_running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() # Ensure the whole game exits

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if shape_rect.collidepoint(event.pos):
                    if is_target_color_active:
                        player_won = True
                    # else: player clicked wrong color, already handled by game_over logic below
                    game_over = True
                    mini_game_running = False # End the loop after click processing
                    break # Exit event loop

        if game_over: # If game ended by click, this will skip color change logic
            continue

        # Color changing logic
        if not is_target_color_active:
            if current_time - last_color_change_time > COLOR_CHANGE_INTERVAL:
                last_color_change_time = current_time
                # Decide if it's time to show the target color
                if random.random() < 0.25 : # 25% chance to become green
                    current_shape_color = TARGET_COLOR
                    is_target_color_active = True
                    target_color_start_time = current_time
                else:
                    current_shape_color = random.choice(OTHER_COLORS)
        else: # Target color is active
            if current_time - target_color_start_time > GREEN_DISPLAY_TIME:
                # Timeout! Player didn't click green in time
                is_target_color_active = False # Reset
                game_over = True
                player_won = False # Timeout means loss
                mini_game_running = False # End the loop


        # --- Drawing ---
        screen.fill((200, 220, 255))  # Light blue background for the mini-game

        pygame.draw.rect(screen, current_shape_color, shape_rect)
        screen.blit(instruction_text, instruction_rect)

        # Display timer if green is active (optional)
        if is_target_color_active and not game_over:
            time_left_ms = GREEN_DISPLAY_TIME - (current_time - target_color_start_time)
            timer_text = font_small.render(f"剩余时间: {time_left_ms // 1000}.{ (time_left_ms % 1000)//100 }s", True, BLACK)
            timer_rect = timer_text.get_rect(center=(screen_width // 2, shape_rect.bottom + 30))
            screen.blit(timer_text, timer_rect)

        pygame.display.flip()
        game_clock.tick(30) # Control FPS

    # --- Game Over Display (briefly show result on mini-game screen) ---
    if player_won:
        final_message_str = "胜利!"
        result_color = GREEN
        reward = 200 # Example reward
    else:
        final_message_str = "失败!"
        result_color = RED
        reward = -50 # Example penalty

    result_text_surface = font_large.render(final_message_str, True, result_color)
    result_rect = result_text_surface.get_rect(center=(screen_width // 2, screen_height // 2))

    screen.fill((200, 220, 255))
    screen.blit(result_text_surface, result_rect)
    pygame.display.flip()
    pygame.time.wait(2000) # Show result for 2 seconds

    return {
        "message": f"反应测试: {final_message_str} (金钱 {reward:+.0f})", # Add sign to reward
        "effect": reward
    }

if __name__ == '__main__':
    # This part is for testing the mini-game standalone
    pygame.init()
    mock_screen_width = 800
    mock_screen_height = 600
    mock_screen = pygame.display.set_mode((mock_screen_width, mock_screen_height))
    pygame.display.set_caption("Mini-Game Standalone Test")

    class MockSettings: # Mock what the game needs from ai_settings
        pass
    mock_ai_settings = MockSettings()

    class MockPlayer: # Mock player
        def __init__(self, name):
            self.player_name = name
            self.money = 1000 # Example
        def invest(self, amount): # Mock invest method
            self.money += amount
            print(f"{self.player_name} new money: {self.money}")

    mock_current_player = MockPlayer("测试玩家")

    # Run the game
    game_result = play(mock_screen, mock_ai_settings, mock_current_player)
    print(f"Mini-game ended. Result: {game_result['message']}, Effect: {game_result['effect']}")

    # Simple loop to keep window open after game finishes, until user quits
    running_test = True
    while running_test:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_test = False
        mock_screen.fill(WHITE) # Clear screen
        end_font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 24)
        end_text = end_font.render(f"游戏结束: {game_result['message']}", True, BLACK)
        end_text_rect = end_text.get_rect(center=(mock_screen_width//2, mock_screen_height//2))
        mock_screen.blit(end_text, end_text_rect)
        pygame.display.flip()

    pygame.quit()
    sys.exit()