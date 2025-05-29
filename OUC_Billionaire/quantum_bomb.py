import numpy as np
import random
import pygame

class Qubit:
    def __init__(self, alpha=1, beta=0):
        self.alpha = complex(alpha)
        self.beta = complex(beta)
        self._normalize()
    
    def _normalize(self):
        norm = np.sqrt(abs(self.alpha)**2 + abs(self.beta)**2)
        if norm > 0:
            self.alpha /= norm
            self.beta /= norm
    
    def copy(self):
        return Qubit(self.alpha, self.beta)
    
    def apply_rotation(self, angle):
        """应用旋转门"""
        cos_half = np.cos(angle/2)
        sin_half = np.sin(angle/2)
        gate = np.array([[cos_half, -sin_half], [sin_half, cos_half]])
        state = np.array([self.alpha, self.beta])
        new_state = gate @ state
        self.alpha, self.beta = complex(new_state[0]), complex(new_state[1])
        self._normalize()
    
    def measure_standard(self):
        """标准基测量"""
        prob_0 = abs(self.alpha)**2
        result = 0 if random.random() < prob_0 else 1
        self.alpha, self.beta = (1, 0) if result == 0 else (0, 1)
        return result
    
    def measure_pm(self):
        """±基测量"""
        plus_amp = (self.alpha + self.beta) / np.sqrt(2)
        prob_plus = abs(plus_amp)**2
        result = 0 if random.random() < prob_plus else 1
        if result == 0:  # |+>
            self.alpha, self.beta = 1/np.sqrt(2), 1/np.sqrt(2)
        else:  # |->
            self.alpha, self.beta = 1/np.sqrt(2), -1/np.sqrt(2)
        return result
    
    def blackbox_test(self, has_bomb):
        """黑箱炸弹检测"""
        if not has_bomb:
            # 没有炸弹：量子比特保持原状态通过
            return False  # 不爆炸
        else:
            # 有炸弹：炸弹对量子比特进行标准基测量
            prob_0 = abs(self.alpha)**2
            result = 0 if random.random() < prob_0 else 1
            
            # 量子比特状态坍缩
            if result == 0:
                self.alpha, self.beta = 1, 0  # 坍缩到|0>
                return False  # 测量到|0>，不爆炸
            else:
                self.alpha, self.beta = 0, 1  # 坍缩到|1>
                return True  # 测量到|1>，爆炸！
    
    def __str__(self):
        return f"({self.alpha:.3f})|0> + ({self.beta:.3f})|1>"

class QuantumBombGame:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 24)
        self.small_font = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 18)
        
        # 颜色
        self.colors = {
            'white': (255, 255, 255), 'black': (0, 0, 0), 'blue': (0, 100, 200),
            'green': (0, 150, 0), 'red': (200, 0, 0), 'orange': (255, 165, 0),
            'gray': (128, 128, 128), 'light_gray': (200, 200, 200)
        }
        
        # 游戏状态
        self.phase = 'select'  # select, operate, judge, result
        self.selected_idx = None
        self.qubit = None
        self.has_bomb = random.choice([True, False])
        self.operations = []
        self.rotation_cards = 15
        self.exploded = False
        self.judgment = None
        self.angle_input = ""
        self.inputting_angle = False
        self.last_measured = False  # 是否刚测量过
        self.display_state = "未知叠加态"  # 显示的状态
        
        # 教程
        self.show_tutorial = False
        self.tutorial_type = 'rules'
        
        print(f"Debug: 炸弹状态 = {self.has_bomb}")
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.inputting_angle:
            if event.key == pygame.K_RETURN:
                try:
                    angle = float(self.angle_input)
                    if 0 <= angle <= 360:
                        self.apply_rotation(np.radians(angle))
                    self.angle_input = ""
                    self.inputting_angle = False
                except ValueError:
                    self.angle_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.angle_input = self.angle_input[:-1]
            elif event.unicode.isdigit() or event.unicode == '.':
                self.angle_input += event.unicode
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self.handle_click(event.pos)
        
        return True  # 默认继续运行
    
    def handle_click(self, pos):
        if self.show_tutorial:
            if self.get_rect(400, 50, 80, 30).collidepoint(pos):
                self.show_tutorial = False
            return True
        
        # 工具栏按钮
        if self.get_rect(20, 20, 60, 25).collidepoint(pos):
            self.show_tutorial = True
            self.tutorial_type = 'rules'
        elif self.get_rect(90, 20, 100, 25).collidepoint(pos):
            if self.player.money >= 50:
                self.player.money -= 50
                self.show_tutorial = True
                self.tutorial_type = 'strategy'
        
        # 主要按钮处理
        if self.phase == 'select':
            for i, rect in enumerate(self.get_qubit_rects()):
                if rect.collidepoint(pos):
                    self.selected_idx = i
                    self.qubit = self.player.qubits[i].copy()
                    self.phase = 'operate'
                    self.last_measured = False
                    self.display_state = "未知叠加态"
                    print(f"Debug: 选择量子比特#{i}, 初始状态={self.qubit}")
                    break
        
        elif self.phase == 'operate':
            buttons = self.get_operation_buttons()
            if buttons['rotate'].collidepoint(pos) and self.rotation_cards > 0:
                self.inputting_angle = True
                self.angle_input = ""
            elif buttons['std_measure'].collidepoint(pos) and self.player.money >= 20:
                self.player.money -= 20
                result = self.qubit.measure_standard()
                self.operations.append(f"标准基测量 → {result}")
                self.last_measured = True
                self.display_state = f"|{result}>"
                print(f"Debug: 标准基测量结果={result}, 量子态={self.qubit}")
            elif buttons['pm_measure'].collidepoint(pos) and self.player.money >= 10:
                self.player.money -= 10
                result = self.qubit.measure_pm()
                basis_result = "|+>" if result == 0 else "|->"
                self.operations.append(f"±基测量 → {basis_result}")
                self.last_measured = True
                self.display_state = basis_result
                print(f"Debug: ±基测量结果={basis_result}, 量子态={self.qubit}")
            elif buttons['blackbox'].collidepoint(pos):
                exploded = self.qubit.blackbox_test(self.has_bomb)
                self.operations.append("黑箱检测完成")
                
                if not self.has_bomb:
                    # 没有炸弹：量子比特保持原状态
                    self.last_measured = False
                    self.display_state = "未知叠加态 (通过黑箱)"
                    print(f"Debug: 黑箱检测 - 无炸弹，量子态保持不变={self.qubit}")
                else:
                    # 有炸弹：量子比特被测量并坍缩
                    if exploded:
                        print(f"Debug: 黑箱检测 - 有炸弹且测量到|1>，爆炸！量子态={self.qubit}")
                        self.exploded = True
                        self.phase = 'result'
                    else:
                        self.last_measured = True
                        # self.display_state = "|0> (炸弹测量结果)"
                        print(f"Debug: 黑箱检测 - 有炸弹但测量到|0>，安全！量子态={self.qubit}")
                        
                if exploded:
                    self.exploded = True
                    self.phase = 'result'
            elif buttons['judge'].collidepoint(pos) and self.operations:
                self.phase = 'judge'
            elif buttons['reselect'].collidepoint(pos):
                self.phase = 'select'
                self.operations = []
                self.last_measured = False
                self.display_state = "未知叠加态"
                print("Debug: 重新选择量子比特")
        
        elif self.phase == 'judge':
            if self.get_rect(300, 400, 100, 40).collidepoint(pos):
                self.judgment = True
                self.phase = 'result'
            elif self.get_rect(420, 400, 100, 40).collidepoint(pos):
                self.judgment = False
                self.phase = 'result'
        
        elif self.phase == 'result':
            if self.get_rect(360, 500, 80, 30).collidepoint(pos):
                return False  # 游戏结束
        
        return True
    
    def apply_rotation(self, angle):
        if self.rotation_cards > 0:
            self.qubit.apply_rotation(angle)
            self.rotation_cards -= 1
            self.operations.append(f"旋转 {np.degrees(angle):.1f}°")
            self.last_measured = False
            self.display_state = "未知叠加态"
            print(f"Debug: 旋转{np.degrees(angle):.1f}度后, 量子态={self.qubit}")
    
    def get_rect(self, x, y, w, h):
        return pygame.Rect(x, y, w, h)
    
    def get_qubit_rects(self):
        return [pygame.Rect(50 + i * 140, 180, 120, 100) for i in range(len(self.player.qubits))]
    
    def get_operation_buttons(self):
        return {
            'rotate': self.get_rect(50, 320, 120, 35),
            'std_measure': self.get_rect(180, 320, 120, 35),
            'pm_measure': self.get_rect(310, 320, 120, 35),
            'blackbox': self.get_rect(440, 320, 120, 35),
            'judge': self.get_rect(50, 370, 120, 35),
            'reselect': self.get_rect(180, 370, 120, 35)
        }
    
    def draw_button(self, rect, text, color=None, enabled=True):
        color = color or (self.colors['gray'] if not enabled else self.colors['blue'])
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.colors['black'], rect, 2)
        text_surf = self.font.render(text, True, self.colors['white'])
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def draw(self):
        self.screen.fill(self.colors['white'])
        
        # 标题和信息
        title = self.font.render("量子炸弹检测游戏", True, self.colors['black'])
        self.screen.blit(title, (20, 60))
        
        info = self.small_font.render(f"积分: {self.player.money} | 旋转机会: {self.rotation_cards}", True, self.colors['black'])
        self.screen.blit(info, (400, 65))
        
        # 工具栏
        self.draw_button(self.get_rect(20, 20, 60, 25), "规则", self.colors['green'])
        self.draw_button(self.get_rect(90, 20, 100, 25), "策略(-50分)", self.colors['orange'])
        
        if self.phase == 'select':
            self.draw_select_phase()
        elif self.phase == 'operate':
            self.draw_operate_phase()
        elif self.phase == 'judge':
            self.draw_judge_phase()
        elif self.phase == 'result':
            self.draw_result_phase()
        
        if self.show_tutorial:
            self.draw_tutorial()
    
    def draw_select_phase(self):
        prompt = self.font.render("选择一个量子比特进行检测:", True, self.colors['black'])
        self.screen.blit(prompt, (50, 150))
        
        for i, (qubit, rect) in enumerate(zip(self.player.qubits, self.get_qubit_rects())):
            prob_1 = abs(qubit.beta)**2
            color = self.colors['green'] if prob_1 < 0.3 else self.colors['orange'] if prob_1 < 0.7 else self.colors['red']
            
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.colors['black'], rect, 2)
            
            text1 = self.small_font.render(f"量子比特 #{i}", True, self.colors['white'])
            text2 = self.small_font.render(f"测出 1 概率:", True, self.colors['white'])
            text3 = self.small_font.render(f"{prob_1:.1%}", True, self.colors['white'])
            
            # 垂直居中的文字布局
            y_start = rect.y + 10
            line_height = 20
            
            self.screen.blit(text1, (rect.x + 8, y_start))
            self.screen.blit(text2, (rect.x + 8, y_start + line_height))
            self.screen.blit(text3, (rect.x + 8, y_start + line_height * 2))
    
    def draw_operate_phase(self):
        state_text = f"当前状态: {self.display_state}"
        state_surf = self.small_font.render(state_text, True, self.colors['black'])
        self.screen.blit(state_surf, (50, 290))
        
        # 操作按钮
        buttons = self.get_operation_buttons()
        self.draw_button(buttons['rotate'], f"旋转({self.rotation_cards})", enabled=self.rotation_cards > 0)
        self.draw_button(buttons['std_measure'], "标准基(-20)", enabled=self.player.money >= 20)
        self.draw_button(buttons['pm_measure'], "±基(-10)", enabled=self.player.money >= 10)
        self.draw_button(buttons['blackbox'], "黑箱检测", self.colors['red'])
        self.draw_button(buttons['judge'], "进行判断", enabled=len(self.operations) > 0)
        self.draw_button(buttons['reselect'], "重新选择", self.colors['gray'])
        
        # 角度输入 - 调整位置
        if self.inputting_angle:
            input_rect = pygame.Rect(50, 420, 200, 30)
            pygame.draw.rect(self.screen, self.colors['white'], input_rect)
            pygame.draw.rect(self.screen, self.colors['blue'], input_rect, 2)
            angle_text = self.font.render(f"角度: {self.angle_input}°", True, self.colors['black'])
            self.screen.blit(angle_text, (input_rect.x + 5, input_rect.y + 5))
        
        # 操作历史 - 调整位置
        if self.operations:
            history_title = self.font.render("操作历史:", True, self.colors['black'])
            self.screen.blit(history_title, (50, 460))
            for i, op in enumerate(self.operations[-5:]):
                op_text = self.small_font.render(f"{i+1}. {op}", True, self.colors['black'])
                self.screen.blit(op_text, (50, 485 + i * 20))
    
    def draw_judge_phase(self):
        prompt = self.font.render("根据操作结果，判断是否有炸弹:", True, self.colors['black'])
        self.screen.blit(prompt, (200, 300))
        
        # 操作摘要
        summary = f"进行了 {len(self.operations)} 次操作"
        summary_surf = self.small_font.render(summary, True, self.colors['black'])
        self.screen.blit(summary_surf, (200, 330))
        
        # 判断按钮
        self.draw_button(self.get_rect(300, 400, 100, 40), "有炸弹", self.colors['red'])
        self.draw_button(self.get_rect(420, 400, 100, 40), "无炸弹", self.colors['green'])
    
    def draw_result_phase(self):
        if self.exploded:
            result_text = "炸弹爆炸！"
            color = self.colors['red']
            message = "黑箱检测触发爆炸\n积分 - 3"
        else:
            correct = (self.judgment == self.has_bomb)
            if correct:
                result_text = "识别正确！"
                color = self.colors['green']
                message = f"实际状态: {'有炸弹' if self.has_bomb else '无炸弹'}\n金钱 + 400！"
            else:
                result_text = "识别错误！"
                color = self.colors['red']
                message = f"你的判断: {'有炸弹' if self.judgment else '无炸弹'}\n实际状态: {'有炸弹' if self.has_bomb else '无炸弹'}\n 积分 - 2"
        
        title_surf = self.font.render(result_text, True, color)
        self.screen.blit(title_surf, (300, 200))
        
        for i, line in enumerate(message.split('\n')):
            line_surf = self.small_font.render(line, True, self.colors['black'])
            self.screen.blit(line_surf, (200, 250 + i * 25))
        
        self.draw_button(self.get_rect(360, 500, 80, 30), "确认", self.colors['blue'])
    
    def draw_tutorial(self):
        # 半透明背景
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(150)
        overlay.fill(self.colors['black'])
        self.screen.blit(overlay, (0, 0))
        
        # 教程窗口
        tutorial_rect = pygame.Rect(100, 100, 600, 400)
        pygame.draw.rect(self.screen, self.colors['white'], tutorial_rect)
        pygame.draw.rect(self.screen, self.colors['blue'], tutorial_rect, 3)
        
        title = "游戏规则" if self.tutorial_type == 'rules' else "策略指南"
        title_surf = self.font.render(title, True, self.colors['blue'])
        self.screen.blit(title_surf, (tutorial_rect.x + 20, tutorial_rect.y + 10))
        
        if self.tutorial_type == 'rules':
            content = [
                "1. 炸弹机制:",
                "   • 有炸弹: 黑箱对量子比特进行标准基测量",
                "   • 测量到|1>则爆炸, 测量到|0>则安全",
                "   • 无炸弹: 量子比特保持原状态通过",
                "2. 操作说明:",
                "   • 旋转: 绕Y轴旋转改变|0>和|1>的概率幅",
                "   • 标准基测量: 强制坍缩到|0>或|1>(-20分)并得知测量结果",
                "   • ±基测量: 在叠加基(|+>, |->)下测量(-10分)",
                "   • 黑箱检测: 炸弹检测, 有风险, 免费",
                "3. 目标: 在不引爆炸弹前提下判断其存在性"
            ]
        else:
            content = [
                "基础策略(50%成功率):",
                "• 发送|+>态进行±基测量",
                "• 哑弹: 输出|+>, 真炸弹: 50%爆炸或输出|+>/|->. 可以通过测量获得一定信息。",
                "",
                "高效策略(理论100%成功率):",
                "• 从|0>开始,每次旋转小角度ε后黑箱检测",
                "• 重复N=π/ε次,爆炸概率仅为O(ε)",
                "• 哑弹: 最终旋转至|1>可检测到",
                "• 真炸弹: 量子Zeno效应锁定在|0>态",
                "• 数学证明: P(爆炸)≤N·sin²(ε/2)=O(ε)"
            ]
        
        for i, line in enumerate(content):
            if line:
                line_surf = self.small_font.render(line, True, self.colors['black'])
                self.screen.blit(line_surf, (tutorial_rect.x + 20, tutorial_rect.y + 50 + i * 25))
        
        self.draw_button(self.get_rect(400, 50, 80, 30), "关闭", self.colors['red'])
    
    def get_result(self):
        """返回游戏结果"""
        if self.exploded:
            return {
                "message": "炸弹爆炸！积分 - 3",
                "effect": 0,
            }
        elif self.judgment == self.has_bomb:
            return {
                "message": "识别正确！获得400金钱奖励",
                "effect": 0,
            }
        else:
            return {
                "message": "识别错误，积分 - 2",
                "effect": 0,
            }

def play(screen, ai_settings, current_player):
    # 确保玩家有必要的属性
    # if not hasattr(current_player, 'qubits'):
    #     current_player.qubits = [
    #         Qubit(1, 0), Qubit(1/np.sqrt(2), 1/np.sqrt(2)), Qubit(0, 1),
    #         Qubit(1/np.sqrt(2), -1/np.sqrt(2)), Qubit(0.8, 0.6)
    #     ]
    current_player.qubits = [
        Qubit(1, 0), Qubit(1/np.sqrt(2), 1/np.sqrt(2)), Qubit(0, 1),
        Qubit(1/np.sqrt(2), -1/np.sqrt(2)), Qubit(0.8, 0.6)
    ]
    if not hasattr(current_player, 'money'):
        current_player.money = 100
    
    # 保存原窗口信息
    original_size = screen.get_size()
    original_caption = pygame.display.get_caption()[0]
    
    try:
        # 创建独立的游戏窗口
        game_screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("量子炸弹检测游戏")
        
        # 创建游戏实例
        game = QuantumBombGame(game_screen, current_player)
        clock = pygame.time.Clock()
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # 用户关闭游戏窗口时，返回默认结果
                    result = {"message": "游戏被关闭", "effect": 0}
                    running = False
                else:
                    running = game.handle_event(event)
            
            if running:  # 只有在游戏还在运行时才绘制
                game.draw()
                pygame.display.flip()
                clock.tick(60)
        
        # 获取游戏结果
        result = game.get_result()
        
    except Exception as e:
        print(f"量子炸弹游戏异常: {e}")
        result = {"message": "游戏异常退出", "effect": 0}
    
    finally:
        # 恢复原窗口
        pygame.display.set_mode(original_size)
        pygame.display.set_caption(original_caption)
        
        # 清空事件队列，避免影响主程序
        pygame.event.clear()
    
    return result

# 测试函数
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("量子炸弹检测游戏")
    
    class MockPlayer:
        def __init__(self):
            self.money = 100
            self.qubits = [
                Qubit(1, 0), Qubit(1/np.sqrt(2), 1/np.sqrt(2)), Qubit(0, 1),
                Qubit(1/np.sqrt(2), -1/np.sqrt(2)), Qubit(0.8, 0.6)
            ]
    
    player = MockPlayer()
    result = play(screen, None, player)
    print(f"游戏结果: {result}")
    pygame.quit()

if __name__ == "__main__":
    main()