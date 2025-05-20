import pygame
import random
import numpy as np
from pygame.locals import *

class QuantumTeleportationGame:
    def __init__(self):
        # 初始化参数与Grover游戏保持一致
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 850  # 与Grover游戏相同的尺寸
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("量子隐形传态 - 抢夺卡小游戏")
        self.clock = pygame.time.Clock()
        
        # 使用相同的颜色定义
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.ORACLE_COLOR = (100, 200, 100)  # 深绿色
        self.DIFFUSION_COLOR = (200, 200, 100)  # 深黄色
        self.CHECK_COLOR = (200, 100, 100)  # 深红色
        
        # 使用相同的字体
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # 游戏状态
        self.state = "intro"  # intro, measuring, gate_selection, result
        self.measurement_result = None
        self.correct_gates = []
        self.player_choices = []
        
        # 贝尔测量结果和对应的正确门操作
        self.bell_states = {
            "Φ⁺": [],
            "Φ⁻": ["Z"],
            "Ψ⁺": ["X"],
            "Ψ⁻": ["X", "Z"]
        }
        
        # 按钮定义（与Grover游戏相似的布局）
        button_height = 50
        self.buttons = {
            "start": pygame.Rect(300, 400, 200, button_height),
            "measure": pygame.Rect(300, 400, 200, button_height),
            "X": pygame.Rect(200, 350, 100, button_height),
            "Z": pygame.Rect(350, 350, 100, button_height),
            "XZ": pygame.Rect(500, 350, 100, button_height),
            "none": pygame.Rect(300, 420, 200, button_height),
            "continue": pygame.Rect(300, 500, 200, button_height)
        }
        
        # 操作反馈变量（与Grover游戏相同）
        self.action_text = ""
        self.show_action_text = False
        self.action_text_time = 0
        self.ACTION_DISPLAY_TIME = 1000  # 显示操作反馈的时间（毫秒）

    def draw_button(self, rect, text, color):
        """与Grover游戏相同的按钮绘制方法"""
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.BLACK, rect, 2)
        text_surf = self.font.render(text, True, self.BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_intro(self):
        """游戏介绍界面"""
        self.screen.fill(self.WHITE)
        
        # 标题（与Grover游戏相同风格）
        title = self.font.render("量子隐形传态协议", True, self.BLUE)
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 100))
        
        # 协议步骤说明（使用相同字体和颜色）
        lines = [
            "你使用了抢夺卡，将执行量子隐形传态协议:",
            "1. 你与目标玩家共享一个EPR对 (|00⟩ + |11⟩)/√2",
            "2. 目标玩家将对其qubit和EPR对进行贝尔测量",
            "3. 你需要根据测量结果选择正确的量子门",
            "4. 正确应用量子门后，你将获得目标qubit"
        ]
        
        for i, line in enumerate(lines):
            text = self.small_font.render(line, True, self.BLACK)
            self.screen.blit(text, (50, 180 + i * 30))
            
        self.draw_button(self.buttons["start"], "开始协议", self.ORACLE_COLOR)
        
        # 显示操作反馈（如果存在）
        if self.show_action_text:
            action_surface = self.font.render(self.action_text, True, self.BLACK)
            self.screen.blit(action_surface, (50, 50))

    def draw_measuring(self):
        """测量阶段界面"""
        self.screen.fill(self.WHITE)
        title = self.font.render("贝尔测量阶段", True, self.BLUE)
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 100))
        
        # 量子电路图示（简化版）
        pygame.draw.line(self.screen, self.BLACK, (200, 200), (600, 200), 2)
        pygame.draw.line(self.screen, self.BLACK, (200, 250), (600, 250), 2)
        pygame.draw.line(self.screen, self.BLACK, (200, 300), (600, 300), 2)
        
        # 绘制贝尔测量符号
        pygame.draw.rect(self.screen, self.DIFFUSION_COLOR, (400, 200, 50, 100))
        measure_text = self.small_font.render("贝尔测量", True, self.BLACK)
        self.screen.blit(measure_text, (405, 240))
        
        self.draw_button(self.buttons["measure"], "进行测量", self.CHECK_COLOR)
        
        if self.show_action_text:
            action_surface = self.font.render(self.action_text, True, self.BLACK)
            self.screen.blit(action_surface, (50, 50))

    def draw_gate_selection(self):
        """门选择界面"""
        self.screen.fill(self.WHITE)
        title = self.font.render("选择量子门", True, self.BLUE)
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 100))
        
        # 显示测量结果（与Grover游戏的反馈风格一致）
        result_text = self.font.render(f"贝尔测量结果: {self.measurement_result}", True, self.BLACK)
        self.screen.blit(result_text, (self.WIDTH//2 - result_text.get_width()//2, 180))
        
        # 门选择说明
        instruction = self.small_font.render("选择需要应用的量子门来恢复量子态:", True, self.BLACK)
        self.screen.blit(instruction, (self.WIDTH//2 - instruction.get_width()//2, 220))
        
        # 绘制门选择按钮（使用与Grover游戏相同的按钮样式）
        self.draw_button(self.buttons["X"], "X门", self.ORACLE_COLOR)
        self.draw_button(self.buttons["Z"], "Z门", self.DIFFUSION_COLOR)
        self.draw_button(self.buttons["XZ"], "X和Z门", self.CHECK_COLOR)
        self.draw_button(self.buttons["none"], "不应用门", self.YELLOW)
        
        if self.show_action_text:
            action_surface = self.font.render(self.action_text, True, self.BLACK)
            self.screen.blit(action_surface, (50, 50))

    def draw_result(self):
        """结果显示界面"""
        self.screen.fill(self.WHITE)
        title = self.font.render("协议结果", True, self.BLUE)
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 100))
        
        # 显示玩家选择和正确答案
        player_choice = "无" if not self.player_choices else "和".join(self.player_choices)
        correct_answer = "无" if not self.correct_gates else "和".join(self.correct_gates)
        
        texts = [
            f"你的选择: {player_choice}",
            f"正确答案: {correct_answer}",
            "",
            "量子隐形传态协议完成!"
        ]
        
        # 结果判定（使用与Grover游戏相同的颜色）
        if set(self.player_choices) == set(self.correct_gates):
            result_text = self.font.render("成功! 你正确恢复了量子态!", True, self.GREEN)
            texts.append("你成功抢夺了目标qubit!")
        else:
            result_text = self.font.render("失败! 量子态恢复不正确!", True, self.RED)
            texts.append("抢夺失败，量子态已损坏!")
            
        self.screen.blit(result_text, (self.WIDTH//2 - result_text.get_width()//2, 180))
        
        # 显示详细信息
        for i, text in enumerate(texts):
            rendered = self.small_font.render(text, True, self.BLACK)
            self.screen.blit(rendered, (self.WIDTH//2 - rendered.get_width()//2, 230 + i * 30))
            
        self.draw_button(self.buttons["continue"], "继续游戏", self.ORACLE_COLOR)
        
        if self.show_action_text:
            action_surface = self.font.render(self.action_text, True, self.BLACK)
            self.screen.blit(action_surface, (50, 50))

    def run(self):
        """运行游戏主循环"""
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            # 检查操作反馈是否超时（与Grover游戏相同逻辑）
            if self.show_action_text and (current_time - self.action_text_time > self.ACTION_DISPLAY_TIME):
                self.show_action_text = False
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.state == "intro" and self.buttons["start"].collidepoint(mouse_pos):
                        self.state = "measuring"
                        self.action_text = "协议初始化!"
                        self.show_action_text = True
                        self.action_text_time = current_time
                        
                    elif self.state == "measuring" and self.buttons["measure"].collidepoint(mouse_pos):
                        # 随机选择贝尔测量结果
                        self.measurement_result = random.choice(list(self.bell_states.keys()))
                        self.correct_gates = self.bell_states[self.measurement_result]
                        self.state = "gate_selection"
                        self.action_text = f"测量结果: {self.measurement_result}"
                        self.show_action_text = True
                        self.action_text_time = current_time
                        
                    elif self.state == "gate_selection":
                        self.player_choices = []
                        if self.buttons["X"].collidepoint(mouse_pos):
                            self.player_choices.append("X")
                            self.action_text = "选择了X门"
                            self.show_action_text = True
                            self.action_text_time = current_time
                        if self.buttons["Z"].collidepoint(mouse_pos):
                            self.player_choices.append("Z")
                            self.action_text = "选择了Z门"
                            self.show_action_text = True
                            self.action_text_time = current_time
                        if self.buttons["XZ"].collidepoint(mouse_pos):
                            self.player_choices.extend(["X", "Z"])
                            self.action_text = "选择了X和Z门"
                            self.show_action_text = True
                            self.action_text_time = current_time
                        if self.buttons["none"].collidepoint(mouse_pos):
                            self.player_choices = []
                            self.action_text = "选择不应用门"
                            self.show_action_text = True
                            self.action_text_time = current_time
                            
                        # 检查是否做出了选择
                        if any(btn.collidepoint(mouse_pos) for btn in [
                            self.buttons["X"], self.buttons["Z"], 
                            self.buttons["XZ"], self.buttons["none"]
                        ]):
                            self.state = "result"
                            
                    elif self.state == "result" and self.buttons["continue"].collidepoint(mouse_pos):
                        return set(self.player_choices) == set(self.correct_gates)
            
            # 绘制当前状态
            if self.state == "intro":
                self.draw_intro()
            elif self.state == "measuring":
                self.draw_measuring()
            elif self.state == "gate_selection":
                self.draw_gate_selection()
            elif self.state == "result":
                self.draw_result()
                
            pygame.display.flip()
            self.clock.tick(30)
            
        pygame.quit()
        return False