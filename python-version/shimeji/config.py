"""
XML Configuration Parser
Parses 動作.xml (actions) and 行動.xml (behaviors)
"""

import ast
import operator
import xml.etree.ElementTree as ET
import os
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class Pose:
    """A single animation frame/pose"""
    image: str
    anchor: Tuple[int, int]  # 基準座標 (x, y)
    velocity: Tuple[int, int]  # 移動速度 (vx, vy)
    duration: int  # 長さ (frames or ms)
    condition: Optional[str] = None


@dataclass
class Animation:
    """Animation sequence containing multiple poses"""
    poses: List[Pose]
    condition: Optional[str] = None


@dataclass
class Action:
    """Action definition from 動作.xml"""
    name: str
    action_type: str  # 種類: 組み込み, 移動, 静止, 固定, 複合, 選択
    frame_type: Optional[str] = None  # 枠: 地面, 壁, 天井
    animations: List[Animation] = None
    sub_actions: List[Dict] = None  # For composite actions
    is_builtin: bool = False
    builtin_class: Optional[str] = None
    params: Dict[str, Any] = None


@dataclass
class BehaviorRef:
    """Reference to another behavior"""
    name: str
    frequency: int
    condition: Optional[str] = None


@dataclass
class Behavior:
    """Behavior definition from 行動.xml"""
    name: str
    frequency: int
    condition: Optional[str] = None
    next_behaviors: List[BehaviorRef] = None
    append: bool = False


class ConfigParser:
    """Parser for mascot configuration files"""
    
    NS = {'m': 'http://www.group-finity.com/Mascot'}
    
    def __init__(self, conf_dir: str = '../conf'):
        self.conf_dir = conf_dir
        self.actions: Dict[str, Action] = {}
        self.behaviors: Dict[str, Behavior] = {}
        self.behavior_conditions: List[Tuple[str, List[Behavior]]] = []
        
    def parse_all(self):
        """Parse all configuration files"""
        self.parse_actions()
        self.parse_behaviors()
        
    def parse_actions(self):
        """Parse 動作.xml"""
        tree = ET.parse(os.path.join(self.conf_dir, '動作.xml'))
        root = tree.getroot()
        
        # Find all action lists
        for action_list in root.findall('m:動作リスト', self.NS):
            for action_elem in action_list.findall('m:動作', self.NS):
                action = self._parse_action(action_elem)
                if action:
                    self.actions[action.name] = action
                    
    def _parse_action(self, elem: ET.Element) -> Optional[Action]:
        """Parse a single action element"""
        name = elem.get('名前')
        action_type = elem.get('種類')
        
        if not name or not action_type:
            return None
            
        action = Action(
            name=name,
            action_type=action_type,
            frame_type=elem.get('枠'),
            animations=[],
            sub_actions=[],
            is_builtin=(action_type == '組み込み'),
            builtin_class=elem.get('クラス'),
            params={}
        )
        
        # Parse parameters
        for attr in ['速度', '重力', '空気抵抗X', '空気抵抗Y', '初速X', '初速Y',
                     '目的地X', '目的地Y', '長さ', 'X', 'Y', '右向き',
                     'IEの端X', 'IEの端Y']:
            if elem.get(attr):
                action.params[attr] = elem.get(attr)
        
        # Parse animations
        if action_type in ['静止', '移動', '固定']:
            for anim_elem in elem.findall('m:アニメーション', self.NS):
                anim = self._parse_animation(anim_elem)
                if anim:
                    action.animations.append(anim)
                    
        # Parse composite actions
        elif action_type in ['複合', '選択']:
            for ref_elem in elem.findall('m:動作参照', self.NS):
                ref = {
                    'name': ref_elem.get('名前'),
                    'params': {}
                }
                for attr in ref_elem.attrib:
                    if attr != '名前':
                        ref['params'][attr] = ref_elem.get(attr)
                action.sub_actions.append(ref)
                
            # Nested actions
            for sub_elem in elem.findall('m:動作', self.NS):
                sub_action = self._parse_action(sub_elem)
                if sub_action:
                    action.sub_actions.append({'nested': sub_action})
                    
        return action
    
    def _parse_animation(self, elem: ET.Element) -> Optional[Animation]:
        """Parse animation element"""
        poses = []
        
        for pose_elem in elem.findall('m:ポーズ', self.NS):
            anchor_str = pose_elem.get('基準座標', '0,0')
            velocity_str = pose_elem.get('移動速度', '0,0')
            
            anchor = tuple(map(int, anchor_str.split(',')))
            velocity = tuple(map(int, velocity_str.split(',')))
            
            pose = Pose(
                image=pose_elem.get('画像', ''),
                anchor=anchor,
                velocity=velocity,
                duration=int(pose_elem.get('長さ', 1)),
                condition=elem.get('条件')
            )
            poses.append(pose)
            
        if poses:
            return Animation(
                poses=poses,
                condition=elem.get('条件')
            )
        return None
        
    def parse_behaviors(self):
        """Parse 行動.xml"""
        tree = ET.parse(os.path.join(self.conf_dir, '行動.xml'))
        root = tree.getroot()
        
        for behavior_list in root.findall('m:行動リスト', self.NS):
            self._parse_behavior_list(behavior_list)
            
    def _parse_behavior_list(self, elem: ET.Element, parent_condition: str = None):
        """Parse behavior list, handling nested conditions"""
        for child in elem:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            
            if tag == '行動':
                behavior = self._parse_behavior(child)
                if behavior:
                    if parent_condition:
                        behavior.condition = parent_condition
                    self.behaviors[behavior.name] = behavior
                    
            elif tag == '条件':
                condition = child.get('条件')
                self._parse_behavior_list(child, condition)
                
    def _parse_behavior(self, elem: ET.Element) -> Optional[Behavior]:
        """Parse a single behavior element"""
        name = elem.get('名前')
        freq_str = elem.get('頻度')
        
        if not name or freq_str is None:
            return None
            
        behavior = Behavior(
            name=name,
            frequency=int(freq_str),
            condition=elem.get('条件'),
            next_behaviors=[],
            append=False
        )
        
        # Parse next behavior list
        next_list = elem.find('m:次の行動リスト', self.NS)
        if next_list is not None:
            behavior.append = next_list.get('追加', 'false').lower() == 'true'
            
            for ref in next_list.findall('m:行動参照', self.NS):
                behavior.next_behaviors.append(BehaviorRef(
                    name=ref.get('名前'),
                    frequency=int(ref.get('頻度', 1)),
                    condition=ref.get('条件')
                ))
                
        return behavior
    
    def get_action(self, name: str) -> Optional[Action]:
        """Get action by name"""
        return self.actions.get(name)
    
    def get_behavior(self, name: str) -> Optional[Behavior]:
        """Get behavior by name"""
        return self.behaviors.get(name)
    
    def get_behaviors_for_condition(self, context: Dict) -> List[Behavior]:
        """Get behaviors that match current context conditions"""
        # This will be expanded with actual condition evaluation
        return list(self.behaviors.values())


class SafeExpressionEvaluator:
    """
    Safe expression evaluator for mascot conditions.
    Replaces dangerous eval() with a restricted expression parser.
    Only allows: math operations, comparisons, and specific mascot/environment properties.
    """
    
    # Allowed operators
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.And: lambda a, b: a and b,
        ast.Or: lambda a, b: a or b,
        ast.Not: operator.not_,
        ast.In: lambda a, b: a in b,
        ast.NotIn: lambda a, b: a not in b,
    }
    
    # Allowed functions (whitelist)
    FUNCTIONS = {
        'abs': abs,
        'max': max,
        'min': min,
        'round': round,
        'len': len,
        'sum': sum,
        'any': any,
        'all': all,
        'bool': bool,
        'int': int,
        'float': float,
        'str': str,
    }
    
    def __init__(self, mascot: Any, environment: Any):
        self.mascot = mascot
        self.environment = environment
        self.math = __import__('math')
        
    def evaluate(self, expr: str) -> Any:
        """Safely evaluate an expression"""
        if not expr or not expr.strip():
            return True
            
        try:
            tree = ast.parse(expr, mode='eval')
            return self._eval_node(tree.body)
        except Exception as e:
            # Log error in debug mode, but return True to not break behavior
            return True
            
    def _eval_node(self, node: ast.AST) -> Any:
        """Recursively evaluate AST nodes"""
        
        # Literals
        if isinstance(node, ast.Constant):
            return node.value
            
        if isinstance(node, ast.Num):  # For Python < 3.8 compatibility
            return node.n
            
        if isinstance(node, ast.Str):  # For Python < 3.8 compatibility
            return node.s
            
        # Name/Variable access
        if isinstance(node, ast.Name):
            return self._get_name_value(node.id)
            
        # Attribute access (e.g., mascot.x)
        if isinstance(node, ast.Attribute):
            obj = self._eval_node(node.value)
            attr_name = node.attr
            
            # Restrict dangerous attributes
            if attr_name.startswith('_'):
                raise ValueError(f"Access to private attribute '{attr_name}' not allowed")
                
            return getattr(obj, attr_name)
            
        # Binary operations (+, -, *, /, etc.)
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.OPERATORS:
                raise ValueError(f"Operator {op_type.__name__} not allowed")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.OPERATORS[op_type](left, right)
            
        # Unary operations (-x, +x, not x)
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.OPERATORS:
                raise ValueError(f"Unary operator {op_type.__name__} not allowed")
            operand = self._eval_node(node.operand)
            return self.OPERATORS[op_type](operand)
            
        # Comparisons
        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left)
            result = True
            for op, comparator in zip(node.ops, node.comparators):
                op_type = type(op)
                if op_type not in self.OPERATORS:
                    raise ValueError(f"Comparison operator {op_type.__name__} not allowed")
                right = self._eval_node(comparator)
                result = result and self.OPERATORS[op_type](left, right)
                left = right
            return result
            
        # Boolean operations (and, or)
        if isinstance(node, ast.BoolOp):
            op_type = type(node.op)
            if op_type not in self.OPERATORS:
                raise ValueError(f"Boolean operator {op_type.__name__} not allowed")
                
            values = [self._eval_node(v) for v in node.values]
            if op_type == ast.And:
                return all(values)
            elif op_type == ast.Or:
                return any(values)
                
        # Function calls
        if isinstance(node, ast.Call):
            func_name = self._get_call_name(node.func)
            
            if func_name not in self.FUNCTIONS:
                raise ValueError(f"Function '{func_name}' not allowed")
                
            args = [self._eval_node(arg) for arg in node.args]
            kwargs = {kw.arg: self._eval_node(kw.value) for kw in node.keywords}
            
            return self.FUNCTIONS[func_name](*args, **kwargs)
            
        # Subscript (e.g., array[0])
        if isinstance(node, ast.Subscript):
            obj = self._eval_node(node.value)
            index = self._eval_node(node.slice)
            return obj[index]
            
        # Tuple/List
        if isinstance(node, (ast.Tuple, ast.List)):
            return [self._eval_node(elt) for elt in node.elts]
            
        # If expression (conditional)
        if isinstance(node, ast.IfExp):
            test = self._eval_node(node.test)
            return self._eval_node(node.body) if test else self._eval_node(node.orelse)
            
        raise ValueError(f"Unsupported expression type: {type(node).__name__}")
        
    def _get_name_value(self, name: str) -> Any:
        """Get value of a named variable"""
        # Whitelist of allowed names
        allowed = {
            'mascot': self.mascot,
            'environment': self.environment,
            'Math': self.math,
            'True': True,
            'False': False,
            'None': None,
        }
        
        if name not in allowed:
            raise ValueError(f"Variable '{name}' not allowed")
            
        return allowed[name]
        
    def _get_call_name(self, func: ast.AST) -> str:
        """Extract function name from call"""
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            # Handle Math.random() etc.
            obj = self._eval_node(func.value)
            if obj is self.math:
                return f"Math.{func.attr}"
            return func.attr
        raise ValueError("Complex function calls not allowed")


def evaluate_condition(condition: str, mascot: Any, environment: Any) -> bool:
    """
    Safely evaluate a condition string like #{mascot.environment.floor.isOn(mascot.anchor)}
    Uses SafeExpressionEvaluator instead of dangerous eval()
    """
    if not condition:
        return True
        
    # Remove #{...} or ${...} wrappers
    if condition.startswith('#{') or condition.startswith('${'):
        condition = condition[2:-1]
        
    # Create evaluator and evaluate
    evaluator = SafeExpressionEvaluator(mascot, environment)
    try:
        result = evaluator.evaluate(condition)
        return bool(result)
    except Exception as e:
        # In case of evaluation error, default to True to not break behavior
        # Log error for debugging if needed
        return True
