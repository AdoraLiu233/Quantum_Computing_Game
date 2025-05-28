import numpy as np

class Gate:
    """量子门基类"""
    def __init__(self, name, matrix):
        self.name = name  # 门的名称，如 "X", "Z", "H"
        self.matrix = matrix  # 门的矩阵表示（使用 NumPy 数组）

    def __str__(self):
        return f"{self.name}-Gate"

    def apply(self, state):
        """应用量子门到量子态（state 是一个 numpy.ndarray）"""
        return np.dot(self.matrix, state)


class XGate(Gate):
    """Pauli-X 门（量子 NOT 门）"""
    def __init__(self):
        # X 门的矩阵表示：[[0, 1], [1, 0]]
        super().__init__("X", np.array([[0, 1], [1, 0]]))


class ZGate(Gate):
    """Pauli-Z 门（相位翻转门）"""
    def __init__(self):
        # Z 门的矩阵表示：[[1, 0], [0, -1]]
        super().__init__("Z", np.array([[1, 0], [0, -1]]))


class HGate(Gate):
    """Hadamard 门（叠加门）"""
    def __init__(self):
        # H 门的矩阵表示：(1/√2) * [[1, 1], [1, -1]]
        h_matrix = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]])
        super().__init__("H", h_matrix)