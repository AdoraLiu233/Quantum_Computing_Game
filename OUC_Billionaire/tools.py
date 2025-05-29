import pygame
import numpy as np
import random
from mini_game_teleportation import QuantumTeleportationGame

class Item:
    """基础道具类"""
    def __init__(self, name, item_type, description):
        self.name = name  # 道具名称
        self.item_type = item_type  # 'good'或'bad'
        self.description = description  # 道具描述
    
    def use(self, player, target_player=None):
        """使用道具的基础方法"""
        raise NotImplementedError("子类必须实现use方法")

    def __str__(self):
        return f"{self.name}: {self.description}"

class UnlimitedMeasurementCard(Item):
    """不限回合测量卡"""
    def __init__(self):
        super().__init__(
            "不限回合测量卡", 
            "good", 
            "可以保留，手里有合适的qubit时再测，得分几率更大"
        )
        self.selecting_qubit = False  # 标记是否正在选择qubit
    
    def use(self, player, qubit_index=None):
        if not player.qubits:
            return False, "没有可测量的量子比特"
        
        if qubit_index is None:
            # 进入选择qubit模式
            self.selecting_qubit = True
            return False, "请点击要测量的量子比特"
        
        # 执行测量
        if 0 <= qubit_index < len(player.qubits):
            try:
                # 修改这里：使用字典方式获取测量结果
                measurement_result = player.measure_qubit(qubit_index)
                outcome = measurement_result['outcome']
                score_change = measurement_result['score_change']
                
                self.selecting_qubit = False
                return True, f"测量结果: {'|1>' if outcome else '|0>'}, 得分变化: {score_change}"
            except Exception as e:
                # 提供更详细的错误信息
                return False, f"使用道具时出错: {str(e)}"
        else:
            return False, f"无效的量子比特索引: {qubit_index} (有效范围: 0-{len(player.qubits)-1})"

class StealCard(Item):
    """抢夺卡(使用量子隐形传态)"""
    def __init__(self):
        super().__init__(
            "抢夺卡", 
            "good", 
            "利用teleportation算法抢夺对方的qubit"
        )
        self.target_player = None
        self.selecting_qubit = None
    
    def use(self, player, target_player=None, selecting_qubit=None):
        if target_player is None:
            return False, "需要选择目标玩家"
        
        if not target_player.qubits:
            return False, "目标玩家没有量子比特"
        
        if selecting_qubit is None:
            return False, "请选择要抢夺的量子比特"
        
        # 这里只是准备阶段，实际抢夺在小游戏成功后执行
        self.target_player = target_player
        self.qubit_index = selecting_qubit
        return True, f"准备抢夺{target_player.player_name}的Q{selecting_qubit+1}"

class RotationCard(Item):
    """任意旋转卡(精确控制版)"""
    def __init__(self):
        # 调用父类的构造函数，传入三个参数
        super().__init__(
            "精确旋转卡", 
            "good", 
            "精确指定旋转角度和目标量子比特"
        )
    
    def use(self, player, target_player=None, qubit_index=None, angle=None):
        if qubit_index is None or angle is None:
            return "需要指定量子比特索引和旋转角度"
        
        if not player.qubits:
            return "没有可旋转的量子比特"
        
        if qubit_index < 0 or qubit_index >= len(player.qubits):
            return "无效的量子比特索引"
        
        # 创建旋转门矩阵
        gate = np.array([
            [np.cos(angle/2), -np.sin(angle/2)],
            [np.sin(angle/2), np.cos(angle/2)]
        ])
        
        player.qubits[qubit_index].apply_gate(gate)
        return (f"已将第{qubit_index}个量子比特旋转{np.degrees(angle)}度\n"
                f"新状态: {player.qubits[qubit_index]}\n"
                f"|1>概率: {abs(player.qubits[qubit_index].beta)**2:.2%}")

class DoubleScoreCard(Item):
    """翻倍卡"""
    def __init__(self):
        super().__init__(
            "翻倍卡", 
            "good", 
            "让下次测量得分翻倍"
        )
        self.active = False
    
    def use(self, player, target_player=None):
        self.active = True
        return "下次测量得分将翻倍"

class DuelCard(Item):
    """对战卡(集成小游戏)"""
    def __init__(self):
        super().__init__(
            "量子对战卡", 
            "good", 
            "发起量子计算挑战小游戏"
        )
    
    # TODO:完善小游戏
    def use(self, player, target_player):
        if not target_player:
            return "需要指定对战玩家"
        
        print("\n=== 量子计算挑战开始 ===")
        print("游戏规则: 快速解答量子计算问题")
        
        # 生成随机量子计算问题
        problems = [
            {"question": "H|0>等于什么?", "answer": "|+>"},
            {"question": "X|1>等于什么?", "answer": "|0>"},
            {"question": "CNOT|00>等于什么?", "answer": "|00>"},
            {"question": "|+>态测量得到|1>的概率是多少?", "answer": "50%"},
            {"question": "量子隐形传态需要多少经典比特?", "answer": "2"}
        ]
        problem = random.choice(problems)
        
        print(f"\n问题: {problem['question']}")
        
        # 玩家回答
        player_answer = input(f"{player.player_name}的答案: ")
        target_answer = input(f"{target_player.player_name}的答案: ")
        
        # 判断胜负
        player_correct = player_answer.lower() == problem['answer'].lower()
        target_correct = target_answer.lower() == problem['answer'].lower()
        
        if player_correct and not target_correct:
            # 玩家赢
            reward = random.choice(["qubit", "score"])
            if reward == "qubit" and target_player.qubits:
                stolen_qubit = target_player.qubits.pop()
                target_player.qubit_count -= 1
                player.qubits.append(stolen_qubit)
                player.qubit_count += 1
                result = f"赢得对战! 获得{target_player.player_name}的一个量子比特"
            else:
                player.score += 2
                result = "赢得对战! 获得2分"
        elif target_correct and not player_correct:
            # 对手赢
            penalty = random.choice(["qubit", "score"])
            if penalty == "qubit" and player.qubits:
                lost_qubit = player.qubits.pop()
                player.qubit_count -= 1
                target_player.qubits.append(lost_qubit)
                target_player.qubit_count += 1
                result = f"输掉对战! 失去一个量子比特给{target_player.player_name}"
            else:
                player.score -= 1
                target_player.score += 1
                result = "输掉对战! 失去1分，对方获得1分"
        else:
            # 平局
            result = "对战平局!"
        
        return (f"\n正确答案: {problem['answer']}\n"
                f"对战结果: {result}")

class DefenseCard(Item):
    """防守卡"""
    def __init__(self):
        super().__init__(
            "防守卡", 
            "good", 
            "抵御对手的抢夺或挑战"
        )
    
    def use(self, player, target_player=None):
        # 这个卡的效果在其他道具使用时检查
        return "已激活防守状态，将抵御下一次攻击"

class ForcedMeasurementCard(Item):
    """强制测量卡(坏道具)"""
    def __init__(self):
        super().__init__(
            "强制测量卡", 
            "bad/good", 
            "必须立即测量随机一个量子比特"
        )
    
    def use(self, player, target_player=None):
        if not player.qubits:
            return "没有可测量的量子比特"
        
        index = random.randint(0, len(player.qubits)-1)
        outcome, score_change = player.measure_qubit(index)
        return f"被迫测量量子比特，结果为{outcome}，得分变化{score_change}"

class FixedRotationCard(Item):
    """指定旋转卡(坏道具改进版)"""
    def __init__(self):
        super().__init__(
            "量子干扰卡", 
            "bad", 
            "随机干扰一个量子比特的状态"
        )
        self.possible_angles = [-np.pi/3, -np.pi/4, -np.pi/6, np.pi/2, np.pi]
    
    def use(self, player, target_player=None):
        if not player.qubits:
            return "没有可干扰的量子比特"
        
        # 随机选择量子比特和旋转角度
        qubit_index = random.randint(0, len(player.qubits)-1)
        angle = random.choice(self.possible_angles)
        
        # 创建旋转门矩阵
        gate = np.array([
            [np.cos(angle/2), -np.sin(angle/2)],
            [np.sin(angle/2), np.cos(angle/2)]
        ])
        
        player.qubits[qubit_index].apply_gate(gate)
        
        return (f"第{qubit_index}个量子比特被随机旋转{np.degrees(angle):.1f}度\n"
                f"新状态: {player.qubits[qubit_index]}\n"
                f"|1>概率: {abs(player.qubits[qubit_index].beta)**2:.2%}")