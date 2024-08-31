from enum import Enum;

class ObstacleType(Enum):
    ReceiverPower = 1
    DeadNode = 2

"""
config for ReceiverPower obstacle:
    > modifier: float (in dB)
    > appliesTo: [Balloon().name, Balloon().name,...]
    > chance: float (0-1)

config for DeadNode obstacle:
    > node: Balloon() (node to be dead)
    > type: "tx" or "rx" or "both"
    > chance: float (0-1)
"""

class Obstacle:
    def __init__(self, obstacle_type, config):
        self.otype = None
        self.config = {}
        
        # set actual value
        self.otype = obstacle_type

        if self.otype == ObstacleType.ReceiverPower:
            if "modifier" not in config:
                raise ValueError("ReceiverPower obstacle must have a modifier")
            if "appliesTo" not in config:
                raise ValueError("ReceiverPower obstacle must have an appliesTo")
            if "chance" not in config:
                raise ValueError("ReceiverPower obstacle must have a chance")
        elif self.otype == ObstacleType.DeadNode:
            if "node" not in config:
                raise ValueError("DeadNode obstacle must have a node")
            if "type" not in config:
                raise ValueError("DeadNode obstacle must have a type")
            if "chance" not in config:
                raise ValueError("DeadNode obstacle must have a chance")

        self.config = config
        