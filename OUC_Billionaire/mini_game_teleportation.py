import pygame
import random
import numpy as np
from pygame.locals import *

def play(screen, gs, ai_settings, qubit_to_steal):
    """主游戏接口，与其他小游戏一致"""
    # 保存主游戏状态
    main_size = screen.get_size()
    main_caption = pygame.display.get_caption()[0]
    
    # 初始化游戏
    game = QuantumTeleportationGame(
        qubit_to_steal=qubit_to_steal,
        screen_size=(1200, 1000)  # 与其他小游戏一致的分辨率
    )
    
    # 运行游戏
    result = game.run()
    
    # 恢复主游戏显示
    screen = pygame.display.set_mode(ai_settings.screen_size)
    pygame.display.set_caption(main_caption)
    
    return {
        "message": result["message"],
        "effect": 100 if result["success"] else 0,
        "success": result["success"]
    }

class QuantumTeleportationGame:
    def __init__(self, qubit_to_steal, screen_size=(800, 850)):
        pygame.init()
        self.WIDTH, self.HEIGHT = screen_size
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("量子隐形传态协议")
        
        # 颜色和字体定义
        self.COLORS = {
            "WHITE": (255, 255, 255),
            "BLACK": (0, 0, 0),
            "GREEN": (0, 255, 0),
            "RED": (255, 0, 0),
            "BLUE": (0, 0, 255),
            "ORACLE": (100, 200, 100),
            "DIFFUSION": (200, 200, 100),
            "CHECK": (200, 100, 100)
        }
        
        try:
            self.font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 24)
            self.small_font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 20)
        except:
            self.font = pygame.font.SysFont(None, 24)
            self.small_font = pygame.font.SysFont(None, 20)
        
        # 游戏状态
        self.state = "intro"  # intro, measuring, gate_selection, result
        self.measurement_result = None
        self.correct_gates = []
        self.player_choices = []
        
        
        # 量子数据
        self.qubit_to_steal = {
            'alpha': qubit_to_steal.alpha,
            'beta': qubit_to_steal.beta
        }
        self.initialize_epr_pair()
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
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
        
    def run(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        self.result = {
            "success": False,
            "effect":0,
            "message": "游戏未完成"
        }
        # print("333333\n")
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    print("666666\n")
                    running = False
                    self.result["message"] = "游戏取消"
                
                if event.type == MOUSEBUTTONDOWN:
                    print("444444\n")
                    self.handle_click(event.pos)
            
            self.draw()
            pygame.display.flip()
            clock.tick(30)
        # print("55555\n")
        return self.result
    
    def handle_click(self, mouse_pos):
        """处理鼠标点击事件"""
        if self.state == "intro" and self.buttons["start"].collidepoint(mouse_pos):
            self.state = "measuring"
            
        elif self.state == "measuring" and self.buttons["measure"].collidepoint(mouse_pos):
            self.perform_measurement()
            
        elif self.state == "gate_selection":
            self.handle_gate_selection(mouse_pos)
            
        elif self.state == "result" and self.buttons["continue"].collidepoint(mouse_pos):
            success = set(self.player_choices) == set(self.correct_gates)
            self.result["success"] = success
            self.result["effect"] = 100 if success else 0
            self.result["message"] = "成功抢夺量子比特！" if success else "抢夺失败！"
            self.state = "exit"  # 标记游戏结束
            self.running = False  # 退出主循环
    
    def perform_measurement(self):
        """执行贝尔测量"""
        bell_states = {
            "Φ+": [],
            "Φ-": ["Z"],
            "Ψ+": ["X"],
            "Ψ-": ["X", "Z"]
        }
        
        # 简化的贝尔测量模拟
        self.measurement_result = random.choice(list(bell_states.keys()))
        self.correct_gates = bell_states[self.measurement_result]
        self.state = "gate_selection"
    
    def handle_gate_selection(self, mouse_pos):
        """处理量子门选择"""
        if self.buttons["X"].collidepoint(mouse_pos):
            self.player_choices.append("X")
        elif self.buttons["Z"].collidepoint(mouse_pos):
            self.player_choices.append("Z")
        elif self.buttons["XZ"].collidepoint(mouse_pos):
            self.player_choices.extend(["X", "Z"])
        elif self.buttons["none"].collidepoint(mouse_pos):
            self.player_choices = []
        
        if any(btn.collidepoint(mouse_pos) for btn in [
            self.buttons["X"], self.buttons["Z"], 
            self.buttons["XZ"], self.buttons["none"]
        ]):
            self.state = "result"
    
    def draw(self):
        """绘制游戏界面"""
        self.screen.fill(self.COLORS["WHITE"])
        
        if self.state == "intro":
            self.draw_intro()
        elif self.state == "measuring":
            self.draw_measuring()
        elif self.state == "gate_selection":
            self.draw_gate_selection()
        elif self.state == "result":
            self.draw_result()
    
    def draw_intro(self):
        """绘制介绍界面"""
        title = self.font.render("量子隐形传态协议", True, self.COLORS["BLUE"])
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 100))
        
        lines = [
            "你使用了抢夺卡，将执行量子隐形传态协议:",
            "1. 你与目标玩家共享一个EPR对 (|00> + |11>)/√2",
            "2. 目标玩家将对其qubit和EPR对进行贝尔测量",
            "3. 你需要根据测量结果选择正确的量子门",
            "4. 正确应用量子门后，你将获得目标qubit"
        ]
        
        for i, line in enumerate(lines):
            text = self.small_font.render(line, True, self.COLORS["BLACK"])
            self.screen.blit(text, (50, 180 + i * 30))
        
        self.draw_button("start", "开始协议", self.COLORS["ORACLE"])
    
    def draw_measuring(self):
        """绘制测量界面"""
        title = self.font.render("贝尔测量阶段", True, self.COLORS["BLUE"])
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 100))
        
        # 绘制量子电路图示
        pygame.draw.rect(self.screen, self.COLORS["DIFFUSION"], (400, 200, 50, 100))
        self.draw_button("measure", "进行测量", self.COLORS["CHECK"])
    
    def draw_gate_selection(self):
        """绘制门选择界面"""
        title = self.font.render("选择量子门", True, self.COLORS["BLUE"])
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 100))
        
        result_text = self.font.render(f"贝尔测量结果: {self.measurement_result}", 
                                     True, self.COLORS["BLACK"])
        self.screen.blit(result_text, (self.WIDTH//2 - result_text.get_width()//2, 180))
        
        self.draw_button("X", "X门", self.COLORS["ORACLE"])
        self.draw_button("Z", "Z门", self.COLORS["DIFFUSION"])
        self.draw_button("XZ", "X和Z门", self.COLORS["CHECK"])
        self.draw_button("none", "不应用门", (200, 200, 100))
    
    def draw_result(self):
        """绘制结果界面"""
        success = set(self.player_choices) == set(self.correct_gates)
        color = self.COLORS["GREEN"] if success else self.COLORS["RED"]
        message = "成功! 你正确恢复了量子态!" if success else "失败! 量子态恢复不正确!"
        
        title = self.font.render("协议结果", True, self.COLORS["BLUE"])
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 100))
        
        result_text = self.font.render(message, True, color)
        self.screen.blit(result_text, (self.WIDTH//2 - result_text.get_width()//2, 180))
        
        self.draw_button("continue", "继续", self.COLORS["ORACLE"])
    
    def draw_button(self, btn_id, text, color):
        """通用按钮绘制方法"""
        btn = self.buttons[btn_id]
        pygame.draw.rect(self.screen, color, btn)
        pygame.draw.rect(self.screen, self.COLORS["BLACK"], btn, 2)
        
        text_surf = self.font.render(text, True, self.COLORS["BLACK"])
        text_rect = text_surf.get_rect(center=btn.center)
        self.screen.blit(text_surf, text_rect)
    
    def initialize_epr_pair(self):
        """初始化EPR对"""
        self.epr_qubit = {
            'alpha': 1/np.sqrt(2),
            'beta': 1/np.sqrt(2)
        }