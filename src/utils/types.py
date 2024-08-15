from typing import Dict, List, Literal, Tuple, TypedDict, Union
import numpy as np

Position = Tuple[int, int]  # Represents (x, y) coordinates
Body = List[List[int]]  # Represents the snake's body
BodyRelative = Tuple[Tuple[int, int], ...]  # Represents the relative positions of body parts
NearBorder = Tuple[bool, bool]  # Represents whether the snake is near the border

class State(TypedDict):
    head: Position
    food: Position
    body: Body
    near_border: NearBorder
    
StateKey = Tuple[int, int, int, BodyRelative, NearBorder]
    
class QTable(TypedDict):
    __root__: Dict[StateKey, np.ndarray]