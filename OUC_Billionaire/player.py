# -*- coding: utf-8 -*-
import pygame
import numpy as np
import random
from tools import UnlimitedMeasurementCard,StealCard

class Player():
    """玩家信息类"""
    def __init__(self, ai_settings, screen, locations, player_id, name, give_starting_items=False):
        self.ai_settings = ai_settings
        self.screen = screen
        self.locations = locations
        
        # 玩家名称
        self.player_name = name
        # 玩家id
        self.player_id = player_id
        # 玩家拥有的金钱数量
        self.money = self.ai_settings.player_init_money
        # 玩家在地图上的初始位置
        self.pos = 0
        # 玩家初始积分
        self.score = 0
        # 玩家道具
        self.items = []
        # 玩家的门
        self.gates = []

        # 量子属性
        self.qubits = []  # 存储玩家拥有的Qubit对象列表
        self.qubit_count = 0  # 拥有的量子比特数量
            
        # 加载图像并获得其外接矩形
        file_path_str = "images/player" + str(player_id) + ".png"
        self.image = pygame.image.load(file_path_str)
        self.rect = self.image.get_rect()
        self.rect.center = (self.locations[0].x, self.locations[0].y)

        if give_starting_items:
            unlimited_card = StealCard()
            self.items.append(unlimited_card)
        
    def move(self, step):
        """控制玩家每回合的移动"""
        self.pos = (self.pos + step) % self.ai_settings.location_cnt
    
    def invest(self, val):
        """控制玩家的投资的收支"""
        self.money += val
        
    def draw_player(self):
        """绘制玩家的位置"""
        self.rect = self.image.get_rect()

        self.pos = self.pos % self.ai_settings.location_cnt

        self.rect.center = (self.locations[self.pos].x, self.locations[self.pos].y)
        self.screen.blit(self.image, self.rect)

    def add_qubit(self, qubit=None):
        """向玩家集合中添加一个量子比特"""
        if qubit is None:
            qubit = Qubit()  # 默认|0>态
        qubit._normalize()
        print("add qubit :",qubit.alpha, qubit.beta)
        self.qubits.append(qubit)
        self.qubit_count += 1

    def remove_qubit(self, index):
        """从玩家集合中移除一个量子比特"""
        if 0 <= index < len(self.qubits):
            self.qubits.pop(index)
            self.qubit_count -= 1
    
    def measure_qubit(self, index):
        """
        增强测量方法
        """
        if 0 <= index < len(self.qubits):
            outcome, score_change = self.qubits[index].measure()
            self.score += score_change
            prob_1 = abs(self.qubits[index].beta)**2
            return {
                'outcome': outcome,
                'score_change': score_change,
                'probability': prob_1,
                'qubit_state_before': str(self.qubits[index]),
                'qubit_index': index
            }
        raise IndexError("量子比特索引越界")

    def get_quantum_state_info(self):
        """返回玩家量子状态的信息"""
        info = {
            'qubit_count': self.qubit_count,
            'score': self.score,
            'qubit_states': [str(qubit) for qubit in self.qubits]
        }
        return info
    
    def add_item(self, item):
        """向玩家集合中添加一个道具"""
        self.items.append(item)

    def add_gate(self, gate):
        self.gates.append(gate)
    
    def use_item(self, item_index, target_player=None, **kwargs):
        """使用道具的增强方法，支持额外参数"""
        if 0 <= item_index < len(self.items):
            item = self.items.pop(item_index)
            return item.use(self, target_player, **kwargs)
        return "无效的道具索引"
    
class Qubit:
    """|0>,|1>为基底"""
    def __init__(self, alpha=None, beta=None):
        """
        初始化为 α|0> + β|1>
        """
        if alpha is None and beta is None:
            # 默认为|0>
            self.alpha = complex(1, 0)
            self.beta = complex(0, 0)
        else:
            self.alpha = complex(alpha)
            self.beta = complex(beta)
            self._normalize()
    
    def _normalize(self):
        """标准化(|α|² + |β|² = 1)"""
        norm = np.sqrt(abs(self.alpha)**2 + abs(self.beta)**2)
        if norm == 0:
            raise ValueError("Zero-norm state vector")
        self.alpha /= norm
        self.beta /= norm
    
    def copy(self):
        return Qubit(self.alpha, self.beta)
    
    def measure(self):
        """
        |0>, |1>为基测量
        返回:
            元组: (0/1结果, 积分变化)
        """
        prob_0 = abs(self.alpha)**2
        outcome = 0 if random.random() < prob_0 else 1
        score_change = -1 if outcome == 0 else 1
        
        # qubit坍缩到经典态
        if outcome == 0:
            self.alpha = complex(1, 0)
            self.beta = complex(0, 0)
        else:
            self.alpha = complex(0, 0)
            self.beta = complex(1, 0)
            
        return outcome, score_change

    def apply_gate(self, gate_matrix):
        new_alpha = gate_matrix[0][0] * self.alpha + gate_matrix[0][1] * self.beta
        new_beta = gate_matrix[1][0] * self.alpha + gate_matrix[1][1] * self.beta
        self.alpha, self.beta = new_alpha, new_beta
        self._normalize()
    
    def __str__(self):
        return f"{self.alpha}|0> + {self.beta}|1>"
    
    # 以下是和量子炸弹游戏相关的属性
    def apply_rotation(self, angle):
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
        if not has_bomb:
            # 没有炸弹：量子比特保持原状态通过
            return False
        else:
            # 有炸弹：炸弹对量子比特进行标准基测量
            prob_0 = abs(self.alpha)**2
            result = 0 if random.random() < prob_0 else 1
            
            # 量子比特状态坍缩
            if result == 0:
                self.alpha, self.beta = 1, 0  # 坍缩到|0>
                return False
            else:
                self.alpha, self.beta = 0, 1  # 坍缩到|1>
                return True
