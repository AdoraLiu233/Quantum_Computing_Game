import pygame
import sys
import random
import math
from typing import Dict

# 初始化pygame
pygame.init()

# 常量定义
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
BLUE = (70, 130, 180)
PURPLE = (147, 112, 219)
GREEN = (60, 179, 113)
RED = (220, 20, 60)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)
DARK_GRAY = (64, 64, 64)
NAVY = (25, 25, 112)

## 确认一下不同量子数应用测量数等于几比较好：不能让玩家有机会枚举了（  但是也要给oracle的随机留够机会

# 字体初始化
try:
    font_title = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 36)
    font_large = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 24)
    font_medium = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 20)
    font_small = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 16)
except:
    font_title = pygame.font.Font(None, 36)
    font_large = pygame.font.Font(None, 24)
    font_medium = pygame.font.Font(None, 20)
    font_small = pygame.font.Font(None, 16)

class QuantumState:
    """简化的量子态类"""
    def __init__(self, n_qubits: int):
        self.n_qubits = n_qubits
        self.register_a = {0: 1.0}  # |000...>
        self.register_b = {0: 1.0}
        self.is_entangled = False
        self.entangled_state = {}
        self.had_final_h = False
        
    def set_input(self, x: int):
        """设置输入状态"""
        print(f"DEBUG: 设置输入状态 x = {bin(x)[2:].zfill(self.n_qubits)}")
        self.register_a = {x: 1.0}
        self.register_b = {0: 1.0}
        self.is_entangled = False
        
    def apply_hadamard_a(self):
        """对寄存器A应用H变换"""
        print(f"DEBUG: 对寄存器A应用Hadamard变换")
        print(f"DEBUG: 变换前 register_a = {self.register_a}")
        
        new_register = {}
        norm_factor = 1.0 / math.sqrt(2 ** self.n_qubits)

        # 对每个可能的输出状态y计算振幅
        for y in range(2 ** self.n_qubits):
            total_amplitude = 0
            
            # 对寄存器A中的每个状态x计算贡献
            for x, amplitude in self.register_a.items():
                # 计算 (-1)^(x·y) 相位因子
                phase = (-1) ** (bin(x & y).count('1'))
                total_amplitude += amplitude * phase * norm_factor
            
            # 只保留非零振幅的状态
            if abs(total_amplitude) > 1e-10:
                new_register[y] = total_amplitude
    
        self.register_a = new_register
        self.had_final_h = True
        print(f"DEBUG: 变换后 register_a = {new_register}")
        print(f"DEBUG: Hadamard变换完成，had_final_h = {self.had_final_h}")
        
    def apply_oracle(self, oracle_func: Dict[int, int]):
        """应用Oracle"""
        print(f"DEBUG: 应用Oracle")
        print(f"DEBUG: Oracle前 register_a = {self.register_a}")
        print(f"DEBUG: Oracle前 register_b = {self.register_b}")
        
        new_state = {}
        for x, amp_a in self.register_a.items():
            for y, amp_b in self.register_b.items():
                fx = oracle_func.get(x, 0)
                new_y = y ^ fx
                key = (x, new_y)
                new_state[key] = new_state.get(key, 0) + amp_a * amp_b
                print(f"DEBUG: Oracle映射 x={bin(x)[2:].zfill(self.n_qubits)} -> f(x)={bin(fx)[2:].zfill(self.n_qubits)}, y={bin(y)[2:].zfill(self.n_qubits)} -> new_y={bin(new_y)[2:].zfill(self.n_qubits)}")
        
        self.entangled_state = new_state
        self.is_entangled = True
        print(f"DEBUG: Oracle后纠缠态 = {new_state}")
        
    def measure_b(self):
        """测量寄存器B"""
        print(f"DEBUG: 开始测量寄存器B")
        if not self.is_entangled:
            print(f"DEBUG: 未纠缠状态，返回B=0")
            return 0, self.register_a
            
        # 计算B的概率分布
        b_probs = {}
        for (x, b), amplitude in self.entangled_state.items():
            b_probs[b] = b_probs.get(b, 0) + abs(amplitude) ** 2
            
        print(f"DEBUG: B寄存器概率分布 = {b_probs}")
        
        # 随机选择测量结果
        b_values = list(b_probs.keys())
        probabilities = list(b_probs.values())
        measured_b = random.choices(b_values, weights=probabilities)[0]
        
        print(f"DEBUG: 测量得到B = {bin(measured_b)[2:].zfill(self.n_qubits)}")
        
        # 坍缩寄存器A
        collapsed_a = {}
        total_prob = 0
        for (x, b), amplitude in self.entangled_state.items():
            if b == measured_b:
                collapsed_a[x] = amplitude
                total_prob += abs(amplitude) ** 2
                print(f"DEBUG: A寄存器坍缩包含状态 x={bin(x)[2:].zfill(self.n_qubits)}, amplitude={amplitude}")
                
        # 归一化
        if total_prob > 0:
            norm_factor = 1.0 / math.sqrt(total_prob)
            for x in collapsed_a:
                collapsed_a[x] *= norm_factor
        
        print(f"DEBUG: 坍缩后A寄存器 = {collapsed_a}")
        
        self.register_a = collapsed_a
        self.is_entangled = False
        return measured_b, collapsed_a
        
    def measure_a(self):
        """测量寄存器A"""
        print(f"DEBUG: 开始测量寄存器A")
        if not self.register_a:
            print(f"DEBUG: A寄存器为空，返回0")
            return 0
            
        probs = {x: abs(amp)**2 for x, amp in self.register_a.items()}
        print(f"DEBUG: A寄存器概率分布 = {probs}")
        x_values = list(probs.keys())
        probabilities = list(probs.values())
        result = random.choices(x_values, weights=probabilities)[0]
        print(f"DEBUG: 测量得到A = {bin(result)[2:].zfill(self.n_qubits)}")
        return result

def gf2_rank(matrix):
    """计算GF(2)矩阵的秩"""
    if not matrix:
        return 0
    
    rows, cols = len(matrix), len(matrix[0])
    rank = 0
    work_matrix = [row[:] for row in matrix]
    
    for col in range(cols):
        # 找主元
        pivot_row = -1
        for row in range(rank, rows):
            if work_matrix[row][col] == 1:
                pivot_row = row
                break
        
        if pivot_row == -1:
            continue
        
        # 交换行
        if pivot_row != rank:
            work_matrix[rank], work_matrix[pivot_row] = work_matrix[pivot_row], work_matrix[rank]
        
        # 消元
        for row in range(rows):
            if row != rank and work_matrix[row][col] == 1:
                for c in range(cols):
                    work_matrix[row][c] ^= work_matrix[rank][c]
        
        rank += 1
    
    return rank

def solve_simon(vectors, n):
    """求解Simon问题"""
    if len(vectors) < n - 1:
        return None
    
    unique_vectors = list(set(vectors))
    matrix = []
    for v in unique_vectors:
        row = [(v >> (n-1-i)) & 1 for i in range(n)]
        matrix.append(row)
        
    rank = gf2_rank(matrix)
    if rank < n - 1:
        return None
    
    # 枚举所有可能解
    for s in range(1, 2**n):
        valid = True
        for v in unique_vectors:
            if bin(s & v).count('1') % 2 != 0:
                valid = False
                break
        if valid:
            return s
    
    return None

def draw_panel(screen, x, y, width, height, title=""):
    """绘制面板"""
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, NAVY, rect, 2)
    
    if title:
        title_surface = font_medium.render(title, True, NAVY)
        screen.blit(title_surface, (x + 10, y + 5))

def draw_button(screen, x, y, width, height, text, color=BLUE, enabled=True):
    """绘制按钮"""
    rect = pygame.Rect(x, y, width, height)
    
    btn_color = color if enabled else LIGHT_GRAY
    pygame.draw.rect(screen, btn_color, rect)
    pygame.draw.rect(screen, DARK_GRAY, rect, 1)
    
    text_color = WHITE if enabled else DARK_GRAY
    text_surface = font_small.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    
    return rect

class SimonGame:
    """简化的Simon算法游戏"""
    def __init__(self, player):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Simon算法游戏")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 游戏参数
        self.n = 3
        self.s = 0
        self.oracle_func = {}
        
        # 游戏状态
        self.quantum_state = QuantumState(self.n)
        self.orthogonal_vectors = []
        self.player = player
        self.oracle_queries = 0
        self.max_queries = self.n * 2
        self.game_won = False
        
        # 测量结果记录
        self.measurement_results = []  # 存储所有测量结果
        self.measurement_round = 0     # 当前测量轮次
        
        # 用户输入
        self.custom_input = ""
        self.input_active = False
        
        # 答案输入
        self.answer_input = ""
        self.answer_input_active = False
        
        # 消息
        self.messages = []
        self.max_messages = 15
        
        # 按钮
        self.button_rects = {}
        
        # 提示是否已购买
        self.hint_purchased = False
        self.oracle_shown = False
        
        self.init_new_game()
        
    def init_new_game(self):
        """初始化新游戏"""
        self.s = random.randint(1, (1 << self.n) - 1)
        print(f"DEBUG: ===== 新游戏开始 =====")
        print(f"DEBUG: 隐藏的s = {bin(self.s)[2:].zfill(self.n)} (十进制: {self.s})")
        
        # 生成Simon Oracle
        self.oracle_func = {}
        processed = set()
        available_outputs = list(range(1 << self.n))
        random.shuffle(available_outputs)
        
        for x in range(1 << self.n):
            if x in processed:
                continue
            x_xor_s = x ^ self.s
            if available_outputs:
                y = available_outputs.pop()
                self.oracle_func[x] = y
                self.oracle_func[x_xor_s] = y
                processed.add(x)
                processed.add(x_xor_s)
        
        print(f"DEBUG: Oracle函数:")
        for x, fx in sorted(self.oracle_func.items()):
            print(f"DEBUG:   f({bin(x)[2:].zfill(self.n)}) = {bin(fx)[2:].zfill(self.n)}")
        
        # 重置状态
        self.quantum_state = QuantumState(self.n)
        self.orthogonal_vectors = []
        self.oracle_queries = 0
        self.max_queries = self.n * 2
        self.game_won = False
        self.custom_input = ""
        self.input_active = False
        self.answer_input = ""
        self.answer_input_active = False
        
        # 重置测量结果
        self.measurement_results = []
        self.measurement_round = 0
        
        self.add_message(f"新游戏开始！n={self.n}", GREEN)
        self.add_message("欢迎自由进行您的探索！", BLUE)
        
    def add_message(self, text, color=NAVY):
        """添加消息"""
        self.messages.append((text, color))
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def use_superposition_input(self):
        """使用叠加态输入"""
        if self.player.money < 10:
            self.add_message("余额不足！", RED)
            return
            
        self.player.money -= 10
        self.quantum_state = QuantumState(self.n)
        self.quantum_state.apply_hadamard_a()
        
        binary_str = "0" * self.n
        self.add_message(f"创建叠加态：H^⊗n|0> = Σ|x>，消耗10金钱", GREEN)
        print(f"DEBUG: 创建叠加态完成")
    
    def use_custom_input(self, x):
        """使用自定义输入"""
        if self.player.money < 15:
            self.add_message("余额不足！", RED)
            return
            
        self.player.money -= 15
        self.quantum_state = QuantumState(self.n)
        self.quantum_state.set_input(x)
        
        x_str = bin(x)[2:].zfill(self.n)
        self.add_message(f"创建纠缠态：|{x_str}>，消耗5金钱", GREEN)
        print(f"DEBUG: 创建自定义输入完成")
    
    def query_oracle(self):
        """查询Oracle"""
        if self.oracle_queries >= self.max_queries:
            self.add_message("Oracle查询次数已用完！", RED)
            return
            
        cost = 0
        if self.player.money < cost:
            self.add_message("余额不足！", RED)
            return
            
        self.player.money -= cost
        self.oracle_queries += 1
        
        print(f"DEBUG: ----- Oracle查询 #{self.oracle_queries} -----")
        self.quantum_state.apply_oracle(self.oracle_func)
        self.add_message(f"Oracle查询 #{self.oracle_queries}", GREEN)
        self.add_message("应用：|x>|0> -> |x>|f(x)>", BLUE)
    
    def measure_b(self):
        """测量寄存器B"""
        cost = 10
        if self.player.money < cost:
            self.add_message("余额不足！", RED)
            return
            
        self.player.money -= cost
        print(f"DEBUG: ----- 测量寄存器B -----")
        measured_b, collapsed_a = self.quantum_state.measure_b()
        
        b_str = bin(measured_b)[2:].zfill(self.n)
        self.add_message(f"测量B结果：({b_str})，消耗10金钱", GREEN)
        
        # 记录测量结果（只要不是全0就记录）
        if measured_b != 0:
            self.measurement_round += 1
            result_entry = {
                'type': 'B',
                'round': self.measurement_round,
                'value': measured_b,
                'oracle_query': self.oracle_queries
            }
            self.measurement_results.append(result_entry)
            print(f"DEBUG: 记录B测量结果: B{self.measurement_round} = {b_str}")
        else:
            print(f"DEBUG: B测量结果为0，不记录")
    
    def apply_final_h(self):
        """应用最终H变换"""
        cost = 5
        if self.player.money < cost:
            self.add_message("余额不足！", RED)
            return
            
        self.player.money -= cost
        print(f"DEBUG: ----- 应用最终Hadamard变换 -----")
        self.quantum_state.apply_hadamard_a()
        self.add_message("对A应用H变换，消耗5金钱", GREEN)
    
    def measure_a(self):
        """测量寄存器A - 使用正确的概率分布"""
        cost = 10
        if self.player.money < cost:
            self.add_message("金钱不足！", RED)
            return
            
        self.player.money -= cost
        
        print(f"DEBUG: ----- 测量寄存器A -----")
        
        # 计算每个状态的概率（振幅的模平方）
        probs = {}
        total_prob = 0
        for x, amplitude in self.quantum_state.register_a.items():
            prob = abs(amplitude) ** 2
            probs[x] = prob
            total_prob += prob
        
        # 归一化概率
        if total_prob > 0:
            for x in probs:
                probs[x] /= total_prob
        
        # 根据概率随机选择
        if probs:
            x_values = list(probs.keys())
            probabilities = list(probs.values())
            measured_y = random.choices(x_values, weights=probabilities)[0]
        else:
            measured_y = 0
        
        had_final_h = self.quantum_state.had_final_h
        
        y_str = bin(measured_y)[2:].zfill(self.n)
        self.add_message(f"测量A得到：({y_str})", GREEN)
        
        # 验证正交性
        dot_product = bin(self.s & measured_y).count('1') % 2
        is_orthogonal = (dot_product == 0)
        
        print(f"DEBUG: 测量结果 y = {y_str}, s·y = {dot_product} (mod 2), 正交性: {is_orthogonal}")
        
        # self.add_message(f"s·y = {dot_product} (mod 2)", GREEN if is_orthogonal else RED)
        
        # 记录测量结果（只要不是全0就记录）
        if measured_y != 0:
            self.measurement_round += 1
            result_entry = {
                'type': 'A',
                'round': self.measurement_round,
                'value': measured_y,
                'oracle_query': self.oracle_queries,
                'is_orthogonal': is_orthogonal
            }
            self.measurement_results.append(result_entry)
            print(f"DEBUG: 记录A测量结果: A{self.measurement_round} = {y_str}")
        else:
            print(f"DEBUG: A测量结果为0，不记录")
        
        # 如果是正交且非零向量，加入向量集合
        if is_orthogonal and measured_y != 0:
            self.orthogonal_vectors.append(measured_y)
            print(f"DEBUG: 添加正交向量到集合: {y_str}")
        elif measured_y == 0:
            self.add_message("测量结果为0，无信息量", GRAY)
        
        # 流程提示
        if had_final_h and not is_orthogonal and not measured_y == 0:
            self.add_message("经过完整Simon算法流程，但没有给出正交向量。可能是数值误差或实现问题。", GOLD)
        
        self.add_message("消耗10金钱", ORANGE)
        
        # 重置量子态
        self.quantum_state = QuantumState(self.n)

    # 计算线性无关向量数量用于按钮启用判断 - 删除此功能
    def get_independent_vector_count(self):
        """获取线性无关向量数量 - 已禁用"""
        return 0  # 始终返回0，禁用自动求解按钮

    def auto_solve(self):
        """自动求解"""
        # 删除自动求解功能
        self.add_message("自动求解功能已禁用，请手动分析结果", ORANGE)
        return
    
    def manual_solve(self, guess_s):
        """手动求解"""
        print(f"DEBUG: ----- 手动求解 -----")
        print(f"DEBUG: 玩家猜测: {bin(guess_s)[2:].zfill(self.n) if guess_s else 'None'}")
        print(f"DEBUG: 正确答案: {bin(self.s)[2:].zfill(self.n)}")
        self.end_game(guess_s)
    
    def end_game(self, solved_s):
        """结束游戏"""
        if solved_s == self.s:
            self.game_won = True
            s_str = bin(self.s)[2:].zfill(self.n)
            bonus = (self.max_queries - self.oracle_queries) * 30
            if self.n == 2:
                self.player.money += bonus + 300
                change = bonus + 300
                self.player.score += 1
            elif self.n == 3:
                self.player.money += bonus + 500
                self.player.score += 2
                change = bonus + 500
            elif self.n == 4:
                self.player.money += bonus + 800
                self.player.score += 3
                change = bonus + 800
            
            print(f"DEBUG: 游戏胜利! s = {s_str}")
            self.add_message("恭喜！找到隐藏字符串！", GOLD)
            self.add_message(f"s = {s_str}", GREEN)
            self.add_message(f"奖励积分{self.n - 1}，奖励金钱{change}", GOLD)
        else:
            s_str = bin(self.s)[2:].zfill(self.n)
            guess_str = bin(solved_s)[2:].zfill(self.n) if solved_s else "无效"
            print(f"DEBUG: 游戏失败! 正确答案: {s_str}, 玩家答案: {guess_str}")
            self.add_message("答案错误！", RED)
            self.add_message(f"你的答案：{guess_str}", RED)
            self.add_message(f"正确答案：{s_str}", GREEN)
    
    def buy_hint(self):
        """购买算法提示"""
        if self.hint_purchased:
            # 显示提示
            self.add_message("策略提示：", BLUE)
            self.add_message("1，创建均匀叠加态（2^n种可能的输入）", GREEN)
            self.add_message("2，使用Oracle，得到纠缠态：Σ|x>|f(x)>", GREEN)
            self.add_message("3，测量寄存器B，随机得到某个函数值y = f(x)", GREEN)
            self.add_message("此时寄存器A坍缩为：(1/√2)(|x> + |x⊕s>)", GREEN)
            self.add_message("4，Hadamard变换——利用量子干涉，", GREEN)
            self.add_message("使垂直于s的向量z测出概率增强", GREEN)
            self.add_message("第5步：测量得到向量y，满足s·y = 0 (mod 2)", GREEN)
            self.add_message("收集n-1个线性无关的正交向量可解出s", GREEN)
            return
            
        cost = 80
        if self.player.money < cost:
            self.add_message("余额不足！需要80 yuan", RED)
            return
            
        self.player.money -= cost
        self.hint_purchased = True
        
        self.add_message("算法提示已购买！可重复查看", BLUE)
        self.add_message("Simon算法能以O(n)次查询，解决需要", BLUE)
        self.add_message("经典算法Ω(√(2^n))次查询的问题，展现了量子优势。", BLUE)
        self.add_message("1，创建均匀叠加态（2^n种可能的输入）", GREEN)
        self.add_message("2，使用Oracle，得到纠缠态：Σ|x>|f(x)>", GREEN)
        self.add_message("3，测量寄存器B，随机得到某个函数值y = f(x)", GREEN)
        self.add_message("此时寄存器A坍缩为：(1/√2)(|x> + |x⊕s>)", GREEN)
        self.add_message("4，Hadamard变换——利用量子干涉，", GREEN)
        self.add_message("使垂直于s的向量z测出概率增强", GREEN)
        self.add_message("第5步：测量得到向量y，满足s·y = 0 (mod 2)", GREEN)
        self.add_message("收集n-1个线性无关的正交向量可解出s", GREEN)
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                for btn_name, rect in self.button_rects.items():
                    if rect.collidepoint(mouse_x, mouse_y):
                        print(f"DEBUG: 点击按钮: {btn_name}")
                        self.handle_button_click(btn_name)
                        
            elif event.type == pygame.KEYDOWN:
                if self.input_active:
                    if event.key == pygame.K_RETURN:
                        try:
                            x_val = int(self.custom_input, 2) if self.custom_input else 0
                            if 0 <= x_val < (1 << self.n):
                                self.use_custom_input(x_val)
                            else:
                                self.add_message("输入超出范围！", RED)
                        except ValueError:
                            self.add_message("请输入有效的二进制数！", RED)
                        self.custom_input = ""
                        self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.custom_input = self.custom_input[:-1]
                    elif event.unicode in '01' and len(self.custom_input) < self.n:
                        self.custom_input += event.unicode
                elif self.answer_input_active:
                    if event.key == pygame.K_RETURN:
                        try:
                            s_val = int(self.answer_input, 2) if self.answer_input else 0
                            if 0 <= s_val < (1 << self.n):
                                self.manual_solve(s_val)
                            else:
                                self.add_message("输入超出范围！", RED)
                        except ValueError:
                            self.add_message("请输入有效的二进制数！", RED)
                        self.answer_input = ""
                        self.answer_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.answer_input = self.answer_input[:-1]
                    elif event.unicode in '01' and len(self.answer_input) < self.n:
                        self.answer_input += event.unicode
                elif event.key == pygame.K_r:
                    self.init_new_game()
    
    def handle_button_click(self, btn_name):
        """处理按钮点击"""
        if btn_name.startswith("n") and btn_name[1:].isdigit():
            new_n = int(btn_name[1:])
            if 2 <= new_n <= 4:
                self.n = new_n
                self.init_new_game()
        elif btn_name == "superposition":
            self.use_superposition_input()
        elif btn_name == "custom":
            self.input_active = True
            self.add_message(f"输入{self.n}位二进制数后按回车：", BLUE)
        elif btn_name == "oracle":
            self.query_oracle()
        elif btn_name == "measure_b":
            self.measure_b()
        elif btn_name == "final_h":
            self.apply_final_h()
        elif btn_name == "measure_a":
            self.measure_a()
        elif btn_name == "auto_solve":
            # 自动求解功能已禁用
            self.add_message("请手动分析测量结果", ORANGE)
        elif btn_name == "manual_solve":
            self.answer_input_active = True
            self.add_message(f"输入{self.n}位二进制答案后按回车：", BLUE)
        elif btn_name == "hint":
            self.buy_hint()
        elif btn_name == "reset":
            self.init_new_game()
    
    def draw(self):
        """绘制游戏界面"""
        self.screen.fill((250, 250, 250))
        
        # 标题
        title_surface = font_title.render("众里寻s千百度", True, NAVY)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 25))
        self.screen.blit(title_surface, title_rect)
        
        # 状态栏
        status = f"金钱:{self.player.money} | Oracle:{self.oracle_queries}/{self.max_queries}"
        if self.game_won:
            status += " | 胜利！"
        status_surface = font_small.render(status, True, NAVY)
        self.screen.blit(status_surface, (20, 50))
        
        # 难度选择
        draw_panel(self.screen, 20, 80, 250, 60, "选择难度")
        for i in range(2, 5):
            color = BLUE if self.n == i else GRAY
            self.button_rects[f"n{i}"] = draw_button(self.screen, 30 + (i-2)*70, 110, 60, 25, 
                                                   f"n={i}", color, not self.game_won)
        
        # 输入选择
        draw_panel(self.screen, 20, 160, 250, 160, "选择输入")
        self.button_rects["superposition"] = draw_button(self.screen, 30, 190, 230, 30, 
                                                       "获得叠加态 (10金钱)", GREEN, 
                                                       self.player.money >= 10 and not self.game_won)
        self.button_rects["custom"] = draw_button(self.screen, 30, 225, 230, 30, 
                                                "获得自定义纠缠态 (15金钱)", BLUE, 
                                                self.player.money >= 15 and not self.game_won)
        
        # 显示输入状态
        if self.input_active:
            # 创建输入框背景
            input_rect = pygame.Rect(30, 265, 230, 25)
            pygame.draw.rect(self.screen, WHITE, input_rect)
            pygame.draw.rect(self.screen, BLUE, input_rect, 2)
            
            # 显示输入内容
            input_text = self.custom_input + "_" if len(self.custom_input) < self.n else self.custom_input
            input_surface = font_medium.render(input_text, True, NAVY)
            self.screen.blit(input_surface, (35, 270))
            
            # 显示提示
            hint_text = f"请输入{self.n}位二进制数 (例: {'0'*(self.n-1)}1)"
            hint_surface = font_small.render(hint_text, True, GRAY)
            self.screen.blit(hint_surface, (30, 295))
        
        # Simon算法步骤 - 位置下移
        draw_panel(self.screen, 20, 340, 250, 200, "Simon算法步骤")
        
        y_pos = 370
        steps = [
            ("oracle", "使用Oracle", GREEN),
            ("measure_b", "测量后寄存器B (10金钱)", PURPLE),
            ("final_h", "对前寄存器使用H变换 (5金钱)", ORANGE),
            ("measure_a", "测量前寄存器A (10金钱)", RED)
        ]
        
        for btn_name, text, color in steps:
            cost = {"oracle": 0, "measure_b": 10, "final_h": 5, "measure_a": 10}[btn_name]
            enabled = (self.player.money >= cost and not self.game_won and 
                      (btn_name != "oracle" or self.oracle_queries < self.max_queries))
            self.button_rects[btn_name] = draw_button(self.screen, 30, y_pos, 230, 30, 
                                                    text, color, enabled)
            y_pos += 35
        
        # 求解工具 - 位置下移
        draw_panel(self.screen, 20, 560, 250, 120, "求解工具")
        # 删除自动求解按钮
        # independent_count = self.get_independent_vector_count()
        # self.button_rects["auto_solve"] = draw_button(self.screen, 30, 590, 110, 30, 
        #                                    "自动求解 (50积分)", GOLD, 
        #                                    self.player.money >= 50 and independent_count >= self.n-1 and not self.game_won)
        self.button_rects["manual_solve"] = draw_button(self.screen, 30, 590, 230, 30, 
                                               "手动输入答案", BLUE, not self.game_won)
        
        # 显示答案输入框
        if self.answer_input_active:
            answer_rect = pygame.Rect(30, 630, 230, 25)
            pygame.draw.rect(self.screen, WHITE, answer_rect)
            pygame.draw.rect(self.screen, BLUE, answer_rect, 2)
            
            answer_text = self.answer_input + "_" if len(self.answer_input) < self.n else self.answer_input
            answer_surface = font_medium.render(answer_text, True, NAVY)
            self.screen.blit(answer_surface, (35, 635))
            
            hint_text = f"输入{self.n}位二进制答案"
            hint_surface = font_small.render(hint_text, True, GRAY)
            self.screen.blit(hint_surface, (30, 660))
        
        self.button_rects["reset"] = draw_button(self.screen, 30, 690, 230, 25, 
                                               "重新开始", GRAY, True)
        
        # 帮助工具 - 位置调整
        draw_panel(self.screen, 20, 720, 250, 60, "帮助工具")
        
        hint_color = BLUE if self.hint_purchased else (BLUE if self.player.money >= 80 else RED)
        hint_text = "查看提示" if self.hint_purchased else "算法提示 (80金钱)"
        self.button_rects["hint"] = draw_button(self.screen, 30, 745, 110, 25, 
                                              hint_text, hint_color, 
                                              self.hint_purchased or self.player.money >= 80)
        
        # 消息面板
        draw_panel(self.screen, 290, 80, 400, 500, "操作日志")
        
        y_pos = 110
        for message, color in self.messages:
            if message:
                text_surface = font_small.render(message, True, color)
                self.screen.blit(text_surface, (310, y_pos))
            y_pos += 18
        
        # 状态面板
        draw_panel(self.screen, 710, 80, 470, 500, "游戏状态")
        
        status_lines = [
            f"难度: n = {self.n}",
            f"目标: 找到{self.n}位隐藏字符串s",
            f"当前金钱: {self.player.money}",
            f"Oracle查询: {self.oracle_queries}/{self.max_queries}",
            "",
            "测量结果:"
        ]
        
        # 显示所有测量结果（按轮次显示）
        for result in self.measurement_results:
            result_type = result['type']
            round_num = result['round']
            value = result['value']
            oracle_query = result['oracle_query']
            value_str = bin(value)[2:].zfill(self.n)
            
            # 简化显示，不显示正交性检查
            status_lines.append(f"{result_type}{round_num}: {value_str} (Oracle#{oracle_query})")
        
        if not self.measurement_results:
            status_lines.append("(暂无测量结果)")
        
        # 删除正交向量和线性无关性显示
        # if self.orthogonal_vectors:
        #     status_lines.append("")
        #     status_lines.append("有效正交向量:")
        #     for i, v in enumerate(self.orthogonal_vectors):
        #         v_str = bin(v)[2:].zfill(self.n)
        #         # 验证显示
        #         dot_check = "√" if bin(self.s & v).count('1') % 2 == 0 else "×"
        #         status_lines.append(f"v{i+1}: {v_str} {dot_check}")
        
        # if self.orthogonal_vectors:
        #     # 检查线性无关性
        #     unique_vectors = list(set(self.orthogonal_vectors))
        #     matrix = []
        #     for v in unique_vectors:
        #         row = [(v >> (self.n-1-i)) & 1 for i in range(self.n)]
        #         matrix.append(row)
        #     rank = gf2_rank(matrix)
        #     status_lines.extend([
        #         "",
        #         f"线性无关向量: {rank}/{self.n-1}",
        #         "√ 可以尝试求解！" if rank >= self.n-1 else "还需要更多向量"
        #     ])
        
        if self.game_won:
            status_lines.extend([
                "",
                "游戏胜利！",
                f"隐藏字符串: {bin(self.s)[2:].zfill(self.n)}"
            ])
        
        y_pos = 110
        for line in status_lines:
            color = GOLD if "胜利" in line or "√" in line else NAVY
            text_surface = font_small.render(line, True, color)
            self.screen.blit(text_surface, (730, y_pos))
            y_pos += 18
        
        # 操作指南
        draw_panel(self.screen, 290, 600, 890, 180, "游戏指南")
        
        guide_lines = [
            "背景故事: 你是一名量子密码学家，发现了一个神秘的黑盒Oracle函数f(x)。",
            "已知线索: f(x) = f(x⊕s)，其中s是隐藏的密钥。你的任务是找出这个密钥！",
            "",
            "操作说明:",
            "创建叠加态：H^⊗n|0> = Σ|x>，同时准备所有2^n种输入",
            "使用Oracle: 应用：|x>|0> -> |x>|f(x)>，其中x是输入",
            "测量操作: 观察量子态，每次测量都会改变系统状态",
            "H变换: 对寄存器A中量子比特采用H门，",
            "效果是H^⊗n|x> = (1/√2^n) ∑_{z∈{0,1}^n} (-1)^(x·z) |z>",
        ]
        
        y_pos = 630
        for line in guide_lines:
            color = GRAY if line else BLACK
            if line:
                text_surface = font_small.render(line, True, color)
                self.screen.blit(text_surface, (310, y_pos))
            y_pos += 15
        
        pygame.display.flip()
    
    def run(self):
        """运行游戏"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# 游戏入口函数
def play(screen, ai_settings, current_player):
    """小游戏入口函数 - 使用独立屏幕"""
    
    # 保存主游戏的屏幕信息
    main_size = (ai_settings.screen_width, ai_settings.screen_height)
    main_caption = pygame.display.get_caption()[0]
    
    # 创建独立的小游戏屏幕（使用您自己调整的尺寸）
    game_screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Simon算法游戏")
    
    # 创建游戏实例，使用独立屏幕
    game = SimonGame(current_player)  # 不传入外部屏幕，让它使用自己的
    
    try:
        # 运行完整的游戏循环
        while game.running:
            game.handle_events()
            game.draw()
            game.clock.tick(60)
        
        # 游戏结束，准备返回结果
        if game.game_won:
            cards = min(6, max(2, game.n + 1))
            result = {
                "message": f"Simon算法挑战成功！",
                "effect": 0
            }
        else:
            result = {
                "message": "Simon算法挑战未完成",
                "effect": 0
            }
    
    except Exception as e:
        print(f"Simon 游戏异常: {e}")
        result = {
            "message": "游戏异常退出",
            "effect": 0
        }
    
    finally:
        # 恢复主游戏屏幕（关键步骤！）
        pygame.display.set_mode(main_size)
        pygame.display.set_caption(main_caption)
    
    return result

def main():
    """主函数 - 独立运行"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    class MockPlayer:
        def __init__(self):
            self.money = 1000
            self.score = 0
    
    player = MockPlayer()
    game = SimonGame(player)
    game.run()

if __name__ == "__main__":
    main()