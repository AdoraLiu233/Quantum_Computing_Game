import sys
import numpy as np
import random
import pygame
import math

class Qubit:
    """量子比特类，与player.py中的保持一致"""
    def __init__(self, alpha=None, beta=None):
        if alpha is None and beta is None:
            self.alpha = complex(1, 0)
            self.beta = complex(0, 0)
        else:
            self.alpha = complex(alpha)
            self.beta = complex(beta)
            self._normalize()
    
    def _normalize(self):
        norm = np.sqrt(abs(self.alpha)**2 + abs(self.beta)**2)
        if norm == 0:
            raise ValueError("Zero-norm state vector")
        self.alpha /= norm
        self.beta /= norm
    
    def copy(self):
        """创建量子比特的副本"""
        return Qubit(self.alpha, self.beta)
    
    def apply_gate(self, gate_matrix):
        """应用量子门"""
        state_vector = np.array([self.alpha, self.beta])
        new_state = gate_matrix @ state_vector
        self.alpha = complex(new_state[0])
        self.beta = complex(new_state[1])
        self._normalize()
    
    def measure_in_standard_basis(self):
        """在{|0>,|1>}基下测量 - 信息最直接，消耗更多积分"""
        prob_0 = abs(self.alpha)**2
        result = 0 if random.random() < prob_0 else 1
        
        # 测量后状态坍缩
        if result == 0:
            self.alpha = complex(1, 0)
            self.beta = complex(0, 0)
        else:
            self.alpha = complex(0, 0)
            self.beta = complex(1, 0)
        
        return result
    
    def measure_in_pm_basis(self):
        """在{|+>,|−>}基下测量 - 信息间接，消耗较少积分"""
        # |+> = (|0> + |1>)/√2, |−> = (|0> - |1>)/√2
        plus_amplitude = (self.alpha + self.beta) / np.sqrt(2)
        prob_plus = abs(plus_amplitude)**2
        
        result = 0 if random.random() < prob_plus else 1  # 0表示|+>，1表示|−>
        
        # 测量后状态坍缩
        if result == 0:  # 测量到|+>
            self.alpha = complex(1/np.sqrt(2), 0)
            self.beta = complex(1/np.sqrt(2), 0)
        else:  # 测量到|−>
            self.alpha = complex(1/np.sqrt(2), 0)
            self.beta = complex(-1/np.sqrt(2), 0)
        
        return result
    
    def measure_in_input_basis(self, bomb_detector):
        """黑箱炸弹检测方法"""
        # 简化的黑箱检测逻辑
        prob_1 = abs(self.beta)**2
        result = 1 if random.random() < prob_1 else 0
        if result == 0:
        # 测量到|0>，状态坍缩为|0>
            self.alpha = complex(1, 0)
            self.beta = complex(0, 0)
        else:
            # 测量到|1>，状态坍缩为|1>
            self.alpha = complex(0, 0)
            self.beta = complex(1, 0)
        return result
    
    def get_display_description(self, measured=False):
        """返回显示给玩家的描述"""
        if measured:
            return str(self)  # 测量后可以显示状态
        else:
            return "未知叠加态 (需要测量才能获取状态信息)"
    
    def __str__(self):
        return f"({self.alpha:.3f})|0> + ({self.beta:.3f})|1>"

class QuantumBombGameUI:
    """优化后的量子炸弹游戏界面类 - 修复重叠问题"""
    
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        
        # 字体初始化
        try:
            self.font_large = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 28)
            self.font_medium = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 20)
            self.font_small = pygame.font.Font('fonts/Noto_Sans_SC.ttf', 16)
        except:
            self.font_large = pygame.font.Font(None, 28)
            self.font_medium = pygame.font.Font(None, 20)
            self.font_small = pygame.font.Font(None, 16)
        
        # 颜色方案
        self.colors = {
            'bg': (248, 249, 250),
            'text': (33, 37, 41),
            'primary': (0, 123, 255),
            'success': (40, 167, 69),
            'danger': (220, 53, 69),
            'warning': (255, 193, 7),
            'info': (23, 162, 184),
            'card_bg': (255, 255, 255),
            'card_border': (206, 212, 218),
            'button_hover': (0, 86, 179),
            'mystery': (108, 117, 125),
            'shadow': (0, 0, 0, 50),
            'panel_bg': (240, 240, 240),
            'white': (255, 255, 255)
        }
        
        # 布局管理器
        self.layout_manager = LayoutManager(self.screen_width, self.screen_height)
        
        # 基础布局参数
        self.layout = {
            'margin': 20,
            'card_spacing': 15,
            'button_width': 120,
            'button_height': 40,
            'small_button_width': 80,
            'small_button_height': 30
        }
        
        self.buttons = {}
        self.qubit_buttons = []
        self.angle_buttons = []
        
        # 预计算固定区域
        self.header_height = 0
        self.info_panel_rect = None
        self.content_area_rect = None
        
    def update_screen_size(self, screen):
        """更新屏幕尺寸并重新计算布局"""
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.layout_manager = LayoutManager(self.screen_width, self.screen_height)
        self.calculate_base_layout()
    
    def calculate_base_layout(self):
        """计算基础布局区域"""
        margin = self.layout['margin']
        
        # 计算头部高度（标题 + 工具栏 + 信息面板）
        title_height = self.font_large.get_height()
        toolbar_height = 35  # 工具栏按钮高度
        info_panel_height = 80
        spacing = 15
        
        self.header_height = margin + title_height + spacing + max(toolbar_height, info_panel_height) + spacing
        
        # 信息面板位置（右上角）
        info_panel_width = 280
        info_x = self.screen_width - info_panel_width - margin
        info_y = margin + title_height + spacing
        self.info_panel_rect = pygame.Rect(info_x, info_y, info_panel_width, info_panel_height)
        
        # 内容区域
        content_y = self.header_height
        self.content_area_rect = pygame.Rect(
            margin, content_y,
            self.screen_width - 2 * margin,
            self.screen_height - content_y - margin
        )
        
        # 重新创建基础按钮
        self.create_base_buttons()
    
    def create_base_buttons(self):
        """创建基础按钮（工具栏）"""
        margin = self.layout['margin']
        title_height = self.font_large.get_height()
        toolbar_y = margin + title_height + 15
        
        # 工具栏按钮（左侧）
        self.buttons['view_rules'] = pygame.Rect(margin, toolbar_y, 80, 30)
        self.buttons['view_strategy'] = pygame.Rect(margin + 90, toolbar_y, 120, 30)
        
        # 教程关闭按钮（会在需要时定位）
        self.buttons['close_tutorial'] = pygame.Rect(
            self.screen_width//2 + 200, 100, 80, 30)
    
    def create_phase_specific_buttons(self, phase, **kwargs):
        """根据游戏阶段创建特定按钮"""
        # 清理阶段特定按钮，保留基础按钮
        keys_to_keep = ['view_rules', 'view_strategy', 'close_tutorial']
        self.buttons = {k: v for k, v in self.buttons.items() if k in keys_to_keep}
        self.qubit_buttons = []
        self.angle_buttons = []
        
        if phase == "select_qubit":
            self.create_qubit_selection_buttons(kwargs.get('qubits', []))
        elif phase == "operation_loop":
            self.create_operation_buttons()
        elif phase == "select_angle":
            self.create_angle_buttons()
        elif phase == "make_judgment":
            self.create_judgment_buttons()
        elif phase in ["show_result", "explosion_result"]:
            self.create_result_buttons()
    
    def create_qubit_selection_buttons(self, qubits):
        """创建量子比特选择按钮"""
        if not qubits or not self.content_area_rect:
            return
        
        # 计算卡片布局
        cols = min(2, len(qubits))
        if cols == 0:
            return
            
        card_spacing = self.layout['card_spacing']
        card_width = (self.content_area_rect.width - card_spacing * (cols + 1)) // cols
        card_height = 80
        
        start_x = self.content_area_rect.x + card_spacing
        start_y = self.content_area_rect.y + 80  # 留出标题空间
        
        for i in range(len(qubits)):
            col = i % cols
            row = i // cols
            
            x = start_x + col * (card_width + card_spacing)
            y = start_y + row * (card_height + card_spacing)
            
            button_rect = pygame.Rect(x, y, card_width, card_height)
            self.qubit_buttons.append((button_rect, i))
    
    def create_operation_buttons(self):
        """创建操作按钮"""
        if not self.content_area_rect:
            return
            
        # 操作按钮放在内容区域的固定位置
        button_area_y = self.content_area_rect.y + 250
        
        btn_width = 140
        btn_height = 45
        spacing = 15
        
        # 第一行：主要操作
        buttons_row1 = ['rotate_qubit', 'measure_standard_basis', 'measure_pm_basis', 'send_to_blackbox']
        for i, btn_name in enumerate(buttons_row1):
            x = self.content_area_rect.x + i * (btn_width + spacing)
            self.buttons[btn_name] = pygame.Rect(x, button_area_y, btn_width, btn_height)
        
        # 第二行：控制按钮
        row2_y = button_area_y + btn_height + 15
        buttons_row2 = ['reselect_qubit', 'make_judgment']
        for i, btn_name in enumerate(buttons_row2):
            x = self.content_area_rect.x + i * (btn_width + spacing)
            self.buttons[btn_name] = pygame.Rect(x, row2_y, btn_width, btn_height)
    
    def create_angle_buttons(self):
        """创建角度选择按钮"""
        if not self.content_area_rect:
            return
            
        angles = [15, 22.5, 30, 45, 60, 90, 120, 135, 150, 180]
        
        # 角度按钮区域
        angle_area_y = self.content_area_rect.y + 150
        
        # 预设角度按钮 - 5列2行
        btn_width = 100
        btn_height = 35
        spacing = 15
        cols = 5
        
        for i, angle in enumerate(angles):
            col = i % cols
            row = i // cols
            
            x = self.content_area_rect.x + col * (btn_width + spacing)
            y = angle_area_y + row * (btn_height + spacing)
            
            button_rect = pygame.Rect(x, y, btn_width, btn_height)
            self.angle_buttons.append((button_rect, np.radians(angle)))
        
        # 自定义角度输入区域
        custom_y = angle_area_y + 120
        self.buttons['custom_angle_input'] = pygame.Rect(
            self.content_area_rect.x, custom_y, 150, 35)
        self.buttons['apply_custom_angle'] = pygame.Rect(
            self.content_area_rect.x + 160, custom_y, 80, 35)
    
    def create_judgment_buttons(self):
        """创建判断按钮"""
        if not self.content_area_rect:
            return
            
        center_x = self.content_area_rect.centerx
        button_y = self.content_area_rect.y + 400
        
        self.buttons['judge_bomb'] = pygame.Rect(
            center_x - 160, button_y, 140, 50)
        self.buttons['judge_no_bomb'] = pygame.Rect(
            center_x + 20, button_y, 140, 50)
    
    def create_result_buttons(self):
        """创建结果按钮"""
        if not self.content_area_rect:
            return
            
        center_x = self.content_area_rect.centerx
        button_y = self.content_area_rect.bottom - 80
        
        self.buttons['confirm_result'] = pygame.Rect(
            center_x - 80, button_y, 140, 45)
    
    def draw_card_with_shadow(self, rect, bg_color, border_color=None, border_width=2):
        """绘制带阴影的卡片"""
        # 阴影
        shadow_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
        shadow_surface = pygame.Surface((rect.width, rect.height))
        shadow_surface.set_alpha(50)
        shadow_surface.fill((0, 0, 0))
        self.screen.blit(shadow_surface, shadow_rect)
        
        # 卡片背景
        pygame.draw.rect(self.screen, bg_color, rect)
        
        # 边框
        if border_color:
            pygame.draw.rect(self.screen, border_color, rect, border_width)
    
    def draw_button(self, rect, text, bg_color, text_color=(255, 255, 255), 
                   font=None, enabled=True):
        """绘制按钮"""
        if font is None:
            font = self.font_small
        
        # 禁用状态的颜色调整
        if not enabled:
            bg_color = (150, 150, 150)
        
        # 绘制按钮
        pygame.draw.rect(self.screen, bg_color, rect)
        pygame.draw.rect(self.screen, self.colors['card_border'], rect, 1)
        
        # 文本
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def draw_header(self, title, player_data=None):
        """绘制页面头部"""
        margin = self.layout['margin']
        
        # 确保布局已计算
        if self.header_height == 0:
            self.calculate_base_layout()
        
        # 清空屏幕（恢复背景清空）
        self.screen.fill(self.colors['bg'])
        
        # 绘制标题
        title_surf = self.font_large.render(title, True, self.colors['primary'])
        self.screen.blit(title_surf, (margin, margin))
        
        # 绘制工具栏按钮
        self.draw_button(self.buttons['view_rules'], "规则", self.colors['primary'])
        self.draw_button(self.buttons['view_strategy'], "策略(-15分)", self.colors['warning'])
        
        # 绘制信息面板
        if player_data and self.info_panel_rect:
            self.draw_info_panel(player_data)
        
        return self.header_height
    
    def draw_complete_interface(self, title, player_data, phase, **kwargs):
        """统一的界面绘制方法 - 防止叠加问题"""
        # 1. 绘制头部（包含屏幕清空）
        self.draw_header(title, player_data)
        
        # 2. 确保为当前阶段创建正确的按钮
        self.create_phase_specific_buttons(phase, **kwargs)
        
        # 3. 根据阶段绘制对应内容（互斥）
        if phase == "select_qubit":
            qubits = kwargs.get('qubits', [])
            if qubits:
                self.draw_qubit_selection(qubits)
        
        elif phase == "operation_loop":
            game_state = kwargs.get('game_state', {})
            self.draw_operation_loop(game_state)
        
        elif phase == "select_angle":
            game_state = kwargs.get('game_state', {})
            self.draw_angle_selection(game_state)
        
        elif phase == "make_judgment":
            operation_history = kwargs.get('operation_history', [])
            self.draw_judgment_phase(operation_history)
        
        elif phase in ["show_result", "explosion_result"]:
            result_data = kwargs.get('result_data', {})
            is_explosion = (phase == "explosion_result")
            self.draw_result_screen(result_data, is_explosion)
        
        # 4. 如果有教程覆盖层，最后绘制
        if kwargs.get('show_tutorial'):
            tutorial_type = kwargs.get('tutorial_type', 'rules')
            scroll_offset = kwargs.get('scroll_offset', 0)
            self.draw_tutorial_overlay(tutorial_type, scroll_offset)
    
    def draw_info_panel(self, player_data):
        """绘制信息面板"""
        if not self.info_panel_rect:
            return
            
        self.draw_card_with_shadow(self.info_panel_rect, self.colors['card_bg'], 
                                 self.colors['card_border'])
        
        # 文本位置
        text_x = self.info_panel_rect.x + 10
        text_y = self.info_panel_rect.y + 10
        
        # 积分
        score_text = f"积分: {player_data.get('score', 0)}"
        score_surf = self.font_small.render(score_text, True, self.colors['text'])
        self.screen.blit(score_surf, (text_x, text_y))
        
        # 资源信息
        resources = player_data.get('resources', {})
        resource_text = f"旋转卡: {resources.get('rotation_cards', 0)} | 检测: {resources.get('blackbox_tests', 0)}次"
        resource_surf = self.font_small.render(resource_text, True, self.colors['text'])
        self.screen.blit(resource_surf, (text_x, text_y + 20))
        
        # 当前量子比特
        if 'current_qubit' in player_data and player_data['current_qubit'] is not None:
            qubit_text = f"当前: 量子比特 #{player_data['current_qubit']}"
            qubit_surf = self.font_small.render(qubit_text, True, self.colors['info'])
            self.screen.blit(qubit_surf, (text_x, text_y + 40))
    
    def draw_qubit_selection(self, qubits):
        """绘制量子比特选择界面"""
        if not self.content_area_rect:
            return
            
        # 标题和提示
        subtitle = self.font_medium.render("选择要进行炸弹检测的量子比特", True, self.colors['text'])
        self.screen.blit(subtitle, (self.content_area_rect.x, self.content_area_rect.y))
        
        hint = self.font_small.render("提示: 选择后将开始实验，需要通过测量获取状态信息", 
                                    True, self.colors['mystery'])
        self.screen.blit(hint, (self.content_area_rect.x, self.content_area_rect.y + 25))
        
        # 量子比特卡片
        for button_rect, qubit_index in self.qubit_buttons:
            if qubit_index < len(qubits):
                qubit = qubits[qubit_index]
                prob_1 = abs(qubit.beta)**2
                
                # 风险评估颜色
                if prob_1 < 0.1:
                    border_color = self.colors['success']
                    risk_text = "低风险"
                elif prob_1 > 0.7:
                    border_color = self.colors['danger']
                    risk_text = "高风险"
                else:
                    border_color = self.colors['warning']
                    risk_text = "中等风险"
                
                # 绘制卡片
                self.draw_card_with_shadow(button_rect, self.colors['card_bg'], 
                                         border_color, 3)
                
                # 量子比特信息
                number_surf = self.font_medium.render(f"量子比特 #{qubit_index}", 
                                                    True, border_color)
                self.screen.blit(number_surf, (button_rect.x + 15, button_rect.y + 10))
                
                state_surf = self.font_small.render(f"状态: {str(qubit)}", 
                                                  True, self.colors['text'])
                self.screen.blit(state_surf, (button_rect.x + 15, button_rect.y + 35))
                
                prob_surf = self.font_small.render(f"|1>概率: {prob_1:.2%} ({risk_text})", 
                                                 True, border_color)
                self.screen.blit(prob_surf, (button_rect.x + 15, button_rect.y + 55))
    
    def draw_operation_loop(self, game_state):
        """绘制操作循环界面"""
        if not self.content_area_rect:
            return
            
        # 状态信息卡片
        status_rect = pygame.Rect(self.content_area_rect.x, self.content_area_rect.y, 
                                self.content_area_rect.width, 120)
        self.draw_card_with_shadow(status_rect, self.colors['card_bg'], 
                                 self.colors['card_border'])
        
        # 当前状态
        if game_state.get('last_measured', False):
            state_text = f"当前状态: {game_state.get('qubit_state', '未知')}"
            state_color = self.colors['text']
        else:
            state_text = "当前状态: 未知叠加态 (需要测量获取信息)"
            state_color = self.colors['mystery']
        
        state_surf = self.font_medium.render(state_text, True, state_color)
        self.screen.blit(state_surf, (status_rect.x + 15, status_rect.y + 15))
        
        # 操作统计
        stats = game_state.get('stats', {})
        stats_text = f"已进行操作: 旋转{stats.get('rotation_count', 0)}次 | " \
                    f"测量{stats.get('measurement_count', 0)}次 | " \
                    f"黑箱检测{stats.get('blackbox_tests', 0)}次"
        stats_surf = self.font_small.render(stats_text, True, self.colors['text'])
        self.screen.blit(stats_surf, (status_rect.x + 15, status_rect.y + 45))
        
        # 提示
        hint_surf = self.font_small.render("可以继续操作或进行最终判断", 
                                         True, self.colors['info'])
        self.screen.blit(hint_surf, (status_rect.x + 15, status_rect.y + 70))
        
        # 操作标题
        op_title = self.font_medium.render("可用操作:", True, self.colors['text'])
        self.screen.blit(op_title, (self.content_area_rect.x, self.content_area_rect.y + 140))
        
        # 操作按钮
        resources = game_state.get('resources', {})
        
        # 第一行按钮
        rotate_enabled = resources.get('rotation_cards', 0) > 0
        self.draw_button(self.buttons['rotate_qubit'], 
                        f"旋转({resources.get('rotation_cards', 0)})", 
                        self.colors['primary'], enabled=rotate_enabled)
        
        self.draw_button(self.buttons['measure_standard_basis'], 
                        "标准基(-20分)", self.colors['warning'])
        
        self.draw_button(self.buttons['measure_pm_basis'], 
                        "±基(-10分)", self.colors['warning'])
        
        self.draw_button(self.buttons['send_to_blackbox'], 
                        "黑箱检测", self.colors['danger'])
        
        # 第二行按钮
        self.draw_button(self.buttons['reselect_qubit'], 
                        "重新选择", self.colors['info'])
        
        history_exists = len(game_state.get('operation_history', [])) > 0
        self.draw_button(self.buttons['make_judgment'], 
                        "进行判断", self.colors['success'], enabled=history_exists)
        
        # 操作历史
        self.draw_operation_history(game_state.get('operation_history', []))
    
    def draw_operation_history(self, history):
        """绘制操作历史"""
        if not history or not self.content_area_rect:
            return
        
        history_y = self.content_area_rect.y + 390
        title_surf = self.font_medium.render("操作历史:", True, self.colors['text'])
        self.screen.blit(title_surf, (self.content_area_rect.x, history_y))
        
        # 显示最近5次操作
        for i, record in enumerate(history[-5:]):
            y_pos = history_y + 30 + i * 22
            
            if record['type'] == 'blackbox_detection':
                text = f"第{record['test_number']}次黑箱检测完成"
                color = self.colors['text']
            elif record['type'] == 'measurement':
                text = f"第{record['measurement_number']}次测量: {record['basis']} → {record['result']}"
                color = self.colors['info']
            elif record['type'] == 'rotation':
                text = f"第{record['rotation_number']}次旋转: {record['angle_degrees']:.1f}度"
                color = self.colors['primary']
            else:
                continue
            
            text_surf = self.font_small.render(text, True, color)
            self.screen.blit(text_surf, (self.content_area_rect.x, y_pos))
    
    def draw_angle_selection(self, game_state):
        """绘制角度选择界面"""
        if not self.content_area_rect:
            return
            
        # 说明
        instruction = self.font_medium.render("选择旋转角度:", True, self.colors['text'])
        self.screen.blit(instruction, (self.content_area_rect.x, self.content_area_rect.y))
        
        hint = self.font_small.render("提示: 小角度多次旋转比大角度一次旋转更安全", 
                                    True, self.colors['mystery'])
        self.screen.blit(hint, (self.content_area_rect.x, self.content_area_rect.y + 25))
        
        # 当前状态
        if game_state.get('last_measured', False):
            state_text = f"当前状态: {game_state.get('qubit_state', '未知')}"
        else:
            state_text = "当前状态: 未知叠加态"
        
        state_surf = self.font_small.render(state_text, True, self.colors['text'])
        self.screen.blit(state_surf, (self.content_area_rect.x, self.content_area_rect.y + 50))
        
        # 预设角度标题
        preset_title = self.font_small.render("预设角度:", True, self.colors['text'])
        self.screen.blit(preset_title, (self.content_area_rect.x, self.content_area_rect.y + 80))
        
        # 角度按钮
        for button_rect, angle in self.angle_buttons:
            angle_deg = np.degrees(angle)
            self.draw_button(button_rect, f"{angle_deg:.1f}°", self.colors['primary'])
        
        # 自定义角度
        custom_title = self.font_small.render("自定义角度 (0-360度):", 
                                            True, self.colors['text'])
        custom_y = self.content_area_rect.y + 270
        self.screen.blit(custom_title, (self.content_area_rect.x, custom_y))
        
        # 输入框
        input_color = self.colors['primary'] if game_state.get('angle_input_active', False) else self.colors['card_border']
        pygame.draw.rect(self.screen, self.colors['card_bg'], self.buttons['custom_angle_input'])
        pygame.draw.rect(self.screen, input_color, self.buttons['custom_angle_input'], 2)
        
        # 修复：显示字符串输入而不是转换后的数字
        angle_text = f"{game_state.get('custom_angle_str', '0')}°"
        angle_surf = self.font_small.render(angle_text, True, self.colors['text'])
        self.screen.blit(angle_surf, (self.buttons['custom_angle_input'].x + 5, 
                                    self.buttons['custom_angle_input'].y + 8))
        
        self.draw_button(self.buttons['apply_custom_angle'], "应用", self.colors['success'])
    
    def draw_judgment_phase(self, operation_history):
        """绘制判断阶段界面"""
        if not self.content_area_rect:
            return
            
        instruction = self.font_medium.render("根据操作结果，判断是否有炸弹：", 
                                            True, self.colors['text'])
        self.screen.blit(instruction, (self.content_area_rect.x, self.content_area_rect.y))
        
        # 操作历史摘要
        if operation_history:
            summary_rect = pygame.Rect(self.content_area_rect.x, self.content_area_rect.y + 40, 
                                     self.content_area_rect.width - 100, 300)
            self.draw_card_with_shadow(summary_rect, self.colors['card_bg'], 
                                     self.colors['card_border'])
            
            # 统计信息
            total_ops = len(operation_history)
            rotation_count = sum(1 for op in operation_history if op['type'] == 'rotation')
            measurement_count = sum(1 for op in operation_history if op['type'] == 'measurement')
            blackbox_count = sum(1 for op in operation_history if op['type'] == 'blackbox_detection')
            
            summary_text = f"总共进行了 {total_ops} 次操作"
            summary_surf = self.font_small.render(summary_text, True, self.colors['text'])
            self.screen.blit(summary_surf, (summary_rect.x + 15, summary_rect.y + 10))
            
            stats_text = f"旋转: {rotation_count}次 | 测量: {measurement_count}次 | 黑箱检测: {blackbox_count}次"
            stats_surf = self.font_small.render(stats_text, True, self.colors['info'])
            self.screen.blit(stats_surf, (summary_rect.x + 15, summary_rect.y + 30))
            
            # 详细历史
            for i, record in enumerate(operation_history[:8]):  # 最多显示8条
                y_pos = summary_rect.y + 60 + i * 20
                
                if record['type'] == 'blackbox_detection':
                    text = f"第{record['test_number']}次黑箱检测完成"
                    color = self.colors['text']
                elif record['type'] == 'measurement':
                    text = f"第{record['measurement_number']}次测量: {record['basis']} → 结果{record['result']}"
                    color = self.colors['info']
                elif record['type'] == 'rotation':
                    text = f"第{record['rotation_number']}次旋转: {record['angle_degrees']:.1f}度"
                    color = self.colors['primary']
                else:
                    continue
                
                text_surf = self.font_small.render(text, True, color)
                self.screen.blit(text_surf, (summary_rect.x + 15, y_pos))
        
        # 判断按钮
        self.draw_button(self.buttons['judge_bomb'], "有炸弹", self.colors['danger'], 
                        font=self.font_medium)
        self.draw_button(self.buttons['judge_no_bomb'], "无炸弹", self.colors['success'], 
                        font=self.font_medium)
    
    def draw_result_screen(self, result_data, is_explosion=False):
        """绘制结果界面"""
        if not self.content_area_rect:
            return
            
        if is_explosion:
            title = "炸弹爆炸！"
            title_color = self.colors['danger']
            card_bg = (255, 245, 245)
        else:
            if result_data.get('outcome') == 'correct':
                title = "恭喜！识别正确"
                title_color = self.colors['success']
                card_bg = (245, 255, 245)
            else:
                title = "识别错误"
                title_color = self.colors['danger']
                card_bg = (255, 245, 245)
        
        # 标题
        title_surf = self.font_large.render(title, True, title_color)
        self.screen.blit(title_surf, (self.content_area_rect.x, self.content_area_rect.y))
        
        # 结果卡片
        result_rect = pygame.Rect(self.content_area_rect.x, self.content_area_rect.y + 50, 
                                self.content_area_rect.width - 100, 300)
        self.draw_card_with_shadow(result_rect, card_bg, title_color, 3)
        
        # 结果消息
        message = result_data.get('message', '无消息')
        lines = message.split('\n')
        for i, line in enumerate(lines[:12]):  # 最多显示12行
            if line.strip():
                line_surf = self.font_small.render(line, True, self.colors['text'])
                self.screen.blit(line_surf, (result_rect.x + 20, result_rect.y + 20 + i * 22))
        
        # 结果按钮
        self.draw_button(self.buttons['confirm_result'], "确认结果", 
                        self.colors['primary'], font=self.font_medium)
    
    def draw_tutorial_overlay(self, tutorial_type, scroll_offset=0):
        """绘制教程覆盖层"""
        # 半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 教程窗口
        tutorial_rect = pygame.Rect(50, 50, self.screen_width - 100, self.screen_height - 100)
        self.draw_card_with_shadow(tutorial_rect, self.colors['card_bg'], 
                                 self.colors['primary'], 3)
        
        # 标题
        if tutorial_type == "rules":
            title = "游戏规则"
            title_color = self.colors['primary']
        else:
            title = "策略教程"
            title_color = self.colors['warning']
        
        title_surf = self.font_large.render(title, True, title_color)
        self.screen.blit(title_surf, (tutorial_rect.x + 20, tutorial_rect.y + 10))
        
        # 内容区域
        content_rect = pygame.Rect(tutorial_rect.x + 10, tutorial_rect.y + 50, 
                                 tutorial_rect.width - 20, tutorial_rect.height - 100)
        
        # 教程内容
        if tutorial_type == "rules":
            content_lines = [
                "基本规则：",
                "1. 选择一个量子比特进行炸弹检测",
                "2. 量子比特状态默认未知，需要通过操作获取信息",
                "3. 可进行的操作：",
                "   • 旋转：改变量子比特状态 (限制10张旋转卡)",
                "   • 测量：获取量子比特状态信息 (消耗积分)",
                "   • 黑箱检测：检测是否有炸弹 (免费但有风险)",
                "4. 可重复进行多次操作",
                "5. 若黑箱检测结果为1且真有炸弹，立即爆炸！",
                "6. 完成操作后进行最终判断",
                "",
                "资源系统：",
                "• 旋转卡：10张可用，可任意角度旋转",
                "• 标准基测量：20积分，直接告诉你是|0>还是|1>",
                "• ±基测量：10积分，告诉你是|+>还是|->",
                "• 黑箱检测：免费，但有爆炸风险",
                "",
                "奖惩机制：",
                "正确识别：退回卡牌 + 获得3张新卡牌",
                "错误识别：下回合跳过移动",
                "检测爆炸：积分减半 + 丢失道具 + 跳过回合"
            ]
        else:
            content_lines = [
                "基础策略：",
                "1. 直接黑箱检测：快速但风险高",
                "2. 先测量后检测：了解状态，降低风险",
                "",
                "改进策略：",
                "1. 使用±基测量了解大致状态",
                "2. 根据测量结果决定是否旋转",
                "3. 旋转90度：将|0>转为|+>状态",
                "4. 进行黑箱检测",
                "",
                "高级策略 (Elitzur-Vaidman)：",
                "1. 多次小角度旋转 (15-30度)",
                "2. 每次旋转后可选择：",
                "   • 继续旋转",
                "   • 标准基测量 (了解精确状态)",
                "   • 黑箱检测",
                "3. 核心思想：渐进式逼近，降低总爆炸概率",
                "",
                "实战技巧：",
                "• 信息收集：合理使用付费测量获取状态信息",
                "• 风险评估：根据已知信息判断爆炸概率",
                "• 渐进策略：小角度多次比大角度一次安全",
                "• 经济平衡：测量成本vs获得信息的价值",
                "• 多轮思维：可重复操作，逐步优化状态"
            ]
        
        # 绘制可滚动内容
        y_start = content_rect.y - scroll_offset
        
        # 设置裁剪区域
        self.screen.set_clip(content_rect)
        
        for i, line in enumerate(content_lines):
            y_pos = y_start + i * 22
            
            # 只绘制可见区域内的文本
            if y_pos > content_rect.y - 30 and y_pos < content_rect.bottom + 30:
                if line.endswith("："):
                    color = self.colors['info']
                    font = self.font_medium
                else:
                    color = self.colors['text']
                    font = self.font_small
                
                if line.strip():
                    text_surf = font.render(line, True, color)
                    self.screen.blit(text_surf, (content_rect.x + 10, y_pos))
        
        # 取消裁剪
        self.screen.set_clip(None)
        
        # 关闭按钮
        self.draw_button(self.buttons['close_tutorial'], "关闭", self.colors['danger'])

class LayoutManager:
    """布局管理器，帮助管理界面元素的位置"""
    
    def __init__(self, screen_width, screen_height, margin=20):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin = margin
        self.current_y = margin
        self.current_x = margin
        
    def reset(self):
        """重置布局位置"""
        self.current_y = self.margin
        self.current_x = self.margin
        
    def next_line(self, height=0, spacing=10):
        """移动到下一行"""
        self.current_y += height + spacing
        self.current_x = self.margin
        return self.current_y
        
    def get_current_pos(self):
        """获取当前位置"""
        return (self.current_x, self.current_y)
        
    def reserve_height(self, height):
        """预留高度空间"""
        self.current_y += height
        
    def get_centered_x(self, width):
        """获取居中的X坐标"""
        return (self.screen_width - width) // 2
        
    def get_right_aligned_x(self, width):
        """获取右对齐的X坐标"""
        return self.screen_width - width - self.margin


class QuantumBombGame:
    def __init__(self, screen, ai_settings, current_player):
        self.screen = screen
        self.ai_settings = ai_settings
        self.current_player = current_player
        self.screen_width, self.screen_height = screen.get_size()
        self.clock = pygame.time.Clock()
        
        # 创建UI管理器
        self.ui = QuantumBombGameUI(screen)
        
        # 游戏状态
        self.game_active = True
        self.game_phase = "select_qubit"
        self.selected_qubit_index = None
        self.test_qubit = None
        self.original_qubit = None
        self.bomb_present = random.choice([True, False])
        print(self.bomb_present)
        
        # 操作状态
        self.blackbox_tests = 0
        self.rotation_count = 0
        self.measurement_count = 0
        
        # 状态追踪
        self.used_rotation_cards = 0
        self.operation_history = []
        self.last_measured = False
        
        # 测试结果
        self.explosion_occurred = False
        self.player_judgment = None
        self.show_tutorial_overlay = False
        self.tutorial_type = "rules"
        self.tutorial_scroll_offset = 0
        
        # 资源系统
        self.rotation_cards_available = 10
        self.tutorial_cost = 15
        self.standard_basis_cost = 20
        self.pm_basis_cost = 10
        
        # 可用的旋转角度
        self.available_angles = [
            np.pi/12, np.pi/8, np.pi/6, np.pi/4, np.pi/3, 
            np.pi/2, 2*np.pi/3, 3*np.pi/4, 5*np.pi/6, np.pi
        ]
        self.custom_angle_str = "0"
        self.angle_input_active = False
        
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.VIDEORESIZE:
                self.screen_width, self.screen_height = event.w, event.h
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
                self.ui.update_screen_size(self.screen)
                
            elif event.type == pygame.MOUSEWHEEL:
                if self.show_tutorial_overlay:
                    self.tutorial_scroll_offset -= event.y * 20
                    self.tutorial_scroll_offset = max(0, min(self.tutorial_scroll_offset, 400))
            
            elif event.type == pygame.KEYDOWN:
                if self.angle_input_active:
                    if event.key == pygame.K_RETURN:
                        self.apply_custom_rotation()
                        self.angle_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        # 修复：正确处理退格键
                        if len(self.custom_angle_str) > 1:
                            self.custom_angle_str = self.custom_angle_str[:-1]
                        else:
                            self.custom_angle_str = "0"
                    elif event.key == pygame.K_ESCAPE:
                        # 新增：ESC键取消输入
                        self.angle_input_active = False
                        self.game_phase = "operation_loop"
                    elif event.unicode.isdigit() or event.unicode == '.':
                        # 修复：更好的数字输入处理
                        if event.unicode == '.' and '.' in self.custom_angle_str:
                            # 防止多个小数点
                            pass
                        elif self.custom_angle_str == "0" and event.unicode.isdigit():
                            # 如果当前是"0"，输入数字时替换而不是追加
                            self.custom_angle_str = event.unicode
                        else:
                            new_str = self.custom_angle_str + event.unicode
                            try:
                                # 验证是否为有效数字且在范围内
                                new_angle = float(new_str)
                                if 0 <= new_angle <= 360:
                                    self.custom_angle_str = new_str
                            except ValueError:
                                pass
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.handle_click(mouse_pos)
    
    def handle_click(self, mouse_pos):
        """处理鼠标点击"""
        # 教程按钮
        if self.ui.buttons['view_rules'].collidepoint(mouse_pos):
            self.show_tutorial_overlay = True
            self.tutorial_type = "rules"
            return
        
        if self.ui.buttons['view_strategy'].collidepoint(mouse_pos):
            if hasattr(self.current_player, 'score') and self.current_player.score >= self.tutorial_cost:
                self.current_player.score -= self.tutorial_cost
                self.show_tutorial_overlay = True
                self.tutorial_type = "strategy"
            else:
                print("积分不足，无法查看策略教程！")
            return
        
        if self.show_tutorial_overlay and self.ui.buttons['close_tutorial'].collidepoint(mouse_pos):
            self.show_tutorial_overlay = False
            self.tutorial_scroll_offset = 0
            return
        
        if self.game_phase == "select_qubit":
            for button_rect, qubit_index in self.ui.qubit_buttons:
                if button_rect.collidepoint(mouse_pos):
                    self.selected_qubit_index = qubit_index
                    self.original_qubit = self.current_player.qubits[qubit_index].copy()
                    self.test_qubit = self.current_player.qubits[qubit_index].copy()
                    self.game_phase = "operation_loop"
                    self.last_measured = False
                    break
                    
        elif self.game_phase == "operation_loop":
            if self.ui.buttons['reselect_qubit'].collidepoint(mouse_pos):
                self.reset_game_state()
                self.game_phase = "select_qubit"
                return
            
            elif self.ui.buttons['make_judgment'].collidepoint(mouse_pos):
                if self.operation_history:
                    self.game_phase = "make_judgment"
                else:
                    print("至少需要进行一次操作！")
                return
                
            elif self.ui.buttons['rotate_qubit'].collidepoint(mouse_pos):
                if self.has_rotation_card():
                    self.game_phase = "select_angle"
                else:
                    print("没有可用的旋转卡！")
            
            elif self.ui.buttons['measure_standard_basis'].collidepoint(mouse_pos):
                if hasattr(self.current_player, 'score') and self.current_player.score >= self.standard_basis_cost:
                    self.current_player.score -= self.standard_basis_cost
                    self.perform_measurement("standard_basis")
                else:
                    print(f"积分不足，无法使用标准基测量！需要{self.standard_basis_cost}积分")
            
            elif self.ui.buttons['measure_pm_basis'].collidepoint(mouse_pos):
                if hasattr(self.current_player, 'score') and self.current_player.score >= self.pm_basis_cost:
                    self.current_player.score -= self.pm_basis_cost
                    self.perform_measurement("pm_basis")
                else:
                    print(f"积分不足，无法使用±基测量！需要{self.pm_basis_cost}积分")
            
            elif self.ui.buttons['send_to_blackbox'].collidepoint(mouse_pos):
                self.perform_blackbox_detection()
                    
        elif self.game_phase == "select_angle":
            if self.ui.buttons['custom_angle_input'].collidepoint(mouse_pos):
                self.angle_input_active = True
                self.custom_angle_str = "0"
                return
            elif self.ui.buttons['apply_custom_angle'].collidepoint(mouse_pos):
                self.apply_custom_rotation()
                return
            
            for button_rect, angle in self.ui.angle_buttons:
                if button_rect.collidepoint(mouse_pos):
                    self.apply_rotation(angle)
                    self.game_phase = "operation_loop"
                    break
                    
        elif self.game_phase == "make_judgment":
            if self.ui.buttons['judge_bomb'].collidepoint(mouse_pos):
                self.player_judgment = True
                self.calculate_final_result()
                self.game_phase = "show_result"
            elif self.ui.buttons['judge_no_bomb'].collidepoint(mouse_pos):
                self.player_judgment = False
                self.calculate_final_result()
                self.game_phase = "show_result"
                
        elif self.game_phase == "show_result" or self.game_phase == "explosion_result":
            if self.ui.buttons['confirm_result'].collidepoint(mouse_pos):
                self.game_active = False
    
    def perform_blackbox_detection(self):
        """执行黑箱炸弹检测"""
        if not self.test_qubit:
            print("错误：没有可检测的量子比特！")
            return
        
        self.blackbox_tests += 1
        
        # 使用|0>态作为炸弹检测器的input基
        bomb_detector = Qubit(1, 0)
        
        # 在黑箱中进行检测
        detection_result = self.test_qubit.measure_in_input_basis(bomb_detector)
        
        # 记录操作历史
        self.operation_history.append({
            'type': 'blackbox_detection',
            'test_number': self.blackbox_tests,
            'result': '检测完成',
            'qubit_state_after': str(self.test_qubit)
        })
        
        self.last_measured = False
        
        print(f"第{self.blackbox_tests}次黑箱检测完成")
        print(f"测量后量子状态：{self.test_qubit}")
        
        # 核心炸弹检测逻辑
        if detection_result == 1 and self.bomb_present:
            self.explosion_occurred = True
            print("炸弹爆炸！")
            self.calculate_explosion_result()
            self.game_phase = "explosion_result"
        else:
            if detection_result == 0:
                print("检测安全")
            else:
                print("检测到异常 - 但炸弹不存在，安全！")
    
    def perform_measurement(self, basis_type):
        """执行测量（消耗积分）"""
        if not self.test_qubit:
            print("错误：没有可测量的量子比特！")
            return
        
        self.measurement_count += 1
        
        if basis_type == "standard_basis":
            measurement_result = self.test_qubit.measure_in_standard_basis()
            basis_name = "{|0>, |1>}"
        elif basis_type == "pm_basis":
            measurement_result = self.test_qubit.measure_in_pm_basis()
            basis_name = "{|+>, |->}"
        
        # 记录操作历史
        self.operation_history.append({
            'type': 'measurement',
            'measurement_number': self.measurement_count,
            'basis': basis_name,
            'result': measurement_result,
            'qubit_state_after': str(self.test_qubit)
        })
        
        self.last_measured = True
        
        print(f"第{self.measurement_count}次测量 - 基: {basis_name}, 结果: {measurement_result}")
        print(f"测量后量子比特状态: {self.test_qubit}")
    
    def apply_rotation(self, angle):
        """应用旋转门"""
        if self.rotation_cards_available > 0:
            # Y旋转门
            rotation_gate = np.array([
                [np.cos(angle/2), -np.sin(angle/2)],
                [np.sin(angle/2), np.cos(angle/2)]
            ])
            self.test_qubit.apply_gate(rotation_gate)
            self.rotation_cards_available -= 1
            self.used_rotation_cards += 1
            self.rotation_count += 1
            
            # 记录操作历史
            self.operation_history.append({
                'type': 'rotation',
                'rotation_number': self.rotation_count,
                'angle_degrees': np.degrees(angle),
                'qubit_state_after': "未知 (旋转后未测量)" if not self.last_measured else str(self.test_qubit)
            })
            
            self.last_measured = False
            
            print(f"已旋转{np.degrees(angle):.1f}度，剩余旋转卡：{self.rotation_cards_available}")
            print(f"旋转后量子状态：{self.test_qubit}")
        else:
            print("没有可用的旋转卡！")
    
    def apply_custom_rotation(self):
        """应用自定义角度旋转"""
        if self.rotation_cards_available > 0:
            try:
                # 修复：从字符串解析角度
                custom_angle = float(self.custom_angle_str) if self.custom_angle_str else 0
                if 0 <= custom_angle <= 360:
                    angle_rad = np.radians(custom_angle)
                    self.apply_rotation(angle_rad)
                    self.game_phase = "operation_loop"
                    self.angle_input_active = False
                else:
                    print("角度必须在0-360度之间！")
                    # 不改变游戏阶段，让用户重新输入
            except ValueError:
                print("请输入有效的角度数值！")
                # 不改变游戏阶段，让用户重新输入
        else:
            print("没有可用的旋转卡！")
            self.game_phase = "operation_loop"
    
    def reset_game_state(self):
        """重置游戏状态，用于重新选择量子比特"""
        self.selected_qubit_index = None
        self.test_qubit = None
        self.original_qubit = None
        self.blackbox_tests = 0
        self.rotation_count = 0
        self.measurement_count = 0
        self.explosion_occurred = False
        self.player_judgment = None
        self.last_measured = False
        
        # 重新生成炸弹状态
        print("重新选择量子比特")
    
    def has_rotation_card(self):
        """检查是否有可用的旋转卡"""
        return self.rotation_cards_available > 0
    
    def calculate_explosion_result(self):
        """计算爆炸的结果"""
        # 应用原量子比特的状态变化
        if self.selected_qubit_index is not None:
            self.current_player.qubits[self.selected_qubit_index] = self.test_qubit.copy()
        
        score_loss = max(self.current_player.score // 2, 0)
        self.current_player.score -= score_loss
        
        self.final_result = {
            "outcome": "explosion",
            "message": f"炸弹爆炸！\n黑箱检测结果为1且确实有炸弹\n积分损失: {score_loss}\n将随机丢失一个道具，下一回合不能移动",
            "score_change": -score_loss,
            "lose_item": True,
            "skip_next_turn": True,
            "explosion_test": self.blackbox_tests,
            "operation_history": self.operation_history
        }
    
    def calculate_final_result(self):
        """根据玩家判断计算最终结果"""
        if self.explosion_occurred:
            return
        
        # 将测试后的量子比特状态返回给玩家
        if self.selected_qubit_index is not None:
            self.current_player.qubits[self.selected_qubit_index] = self.test_qubit.copy()
        
        correct_judgment = (self.player_judgment == self.bomb_present)
        
        if correct_judgment:
            self.final_result = {
                "outcome": "correct",
                "message": f"正确识别炸弹状态！\n实际状态：{'有炸弹' if self.bomb_present else '无炸弹'}\n使用的{self.used_rotation_cards}张旋转卡全部退回\n并可自选3张新卡牌",
                "score_change": 0,
                "return_cards": self.used_rotation_cards,
                "select_new_cards": 3
            }
        else:
            judgment_text = "有炸弹" if self.player_judgment else "无炸弹"
            actual_text = "有炸弹" if self.bomb_present else "无炸弹"
            self.final_result = {
                "outcome": "wrong",
                "message": f"错误识别！\n你的判断：{judgment_text}\n实际状态：{actual_text}\n被视为爆炸案同伙，下一回合无法移动",
                "score_change": 0,
                "skip_next_turn": True
            }
    
    def draw(self):
        """绘制游戏界面"""
        # 准备数据
        player_data = {
            'score': getattr(self.current_player, 'score', 0),
            'resources': {
                'rotation_cards': self.rotation_cards_available,
                'blackbox_tests': self.blackbox_tests
            },
            'current_qubit': self.selected_qubit_index
        }
        
        # 绘制头部
        self.ui.draw_header("量子炸弹测试 (Elitzur-Vaidman)", player_data)
        
        # 根据阶段绘制内容和创建按钮
        if self.game_phase == "select_qubit":
            self.ui.create_phase_specific_buttons("select_qubit", 
                                                qubits=getattr(self.current_player, 'qubits', []))
            self.ui.draw_qubit_selection(getattr(self.current_player, 'qubits', []))
        
        elif self.game_phase == "operation_loop":
            self.ui.create_phase_specific_buttons("operation_loop")
            game_state = {
                'last_measured': self.last_measured,
                'qubit_state': str(self.test_qubit) if self.test_qubit else '',
                'stats': {
                    'rotation_count': self.rotation_count,
                    'measurement_count': self.measurement_count,
                    'blackbox_tests': self.blackbox_tests
                },
                'resources': {'rotation_cards': self.rotation_cards_available},
                'operation_history': self.operation_history
            }
            self.ui.draw_operation_loop(game_state)
        
        elif self.game_phase == "select_angle":
            self.ui.create_phase_specific_buttons("select_angle")
            game_state = {
                'last_measured': self.last_measured,
                'qubit_state': str(self.test_qubit) if self.test_qubit else '',
                'custom_angle_str': self.custom_angle_str,
                'angle_input_active': self.angle_input_active
            }
            self.ui.draw_angle_selection(game_state)
        
        elif self.game_phase == "make_judgment":
            self.ui.create_phase_specific_buttons("make_judgment")
            self.ui.draw_judgment_phase(self.operation_history)
        
        elif self.game_phase == "show_result":
            self.ui.create_phase_specific_buttons("show_result")
            if hasattr(self, 'final_result'):
                self.ui.draw_result_screen(self.final_result, is_explosion=False)
        
        elif self.game_phase == "explosion_result":
            self.ui.create_phase_specific_buttons("explosion_result")
            if hasattr(self, 'final_result'):
                self.ui.draw_result_screen(self.final_result, is_explosion=True)
        
        # 教程覆盖层
        if self.show_tutorial_overlay:
            self.ui.draw_tutorial_overlay(self.tutorial_type, self.tutorial_scroll_offset)
    
    def run(self):
        """运行游戏主循环"""
        while self.game_active:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)
        
        # 返回结果
        if hasattr(self, 'final_result'):
            return {
                "message": self.final_result["message"],
                "effect": self.final_result.get("score_change", 0),
                "skip_turn": self.final_result.get("skip_next_turn", False),
                "lose_item": self.final_result.get("lose_item", False),
                "return_cards": self.final_result.get("return_cards", 0),
                "new_cards": self.final_result.get("select_new_cards", 0)
            }
        else:
            return {"message": "游戏未完成", "effect": 0}


def play(screen, ai_settings, current_player):
    """小游戏入口函数，与现有框架兼容"""
    game = QuantumBombGame(screen, ai_settings, current_player)
    return game.run()


# 测试用的独立运行函数
def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 750), pygame.RESIZABLE)
    pygame.display.set_caption("量子炸弹测试 - 科学实验版")
    
    # 模拟玩家和设置
    class MockPlayer:
        def __init__(self):
            self.score = 100
            self.qubits = [
                Qubit(1, 0),  # |0>
                Qubit(1/np.sqrt(2), 1/np.sqrt(2)),  # |+>
                Qubit(0, 1),  # |1>
                Qubit(1/np.sqrt(2), -1/np.sqrt(2)),  # |−>
                Qubit(0.8, 0.6),  # 自定义态
            ]
    
    class MockSettings:
        pass
    
    player = MockPlayer()
    settings = MockSettings()
    
    result = play(screen, settings, player)
    print(f"游戏结果: {result}")
    
    pygame.quit()

if __name__ == "__main__":
    main()