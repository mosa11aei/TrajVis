from TrajVis.components.defaults import *
from TrajVis.components.obstacle import ObstacleType
import networkx as nx
import copy
import random

class Network:
    nodes = []
    connections = {}
    cg = nx.DiGraph()
    message_queue = {}
    stored = []
    forwarded = 0
    THRESHHOLD = 3 # in dB
    reconfigures = []
    start_node = ''
    end_node = ''
    path = []
    generic_path = []
    path_weight = 0
    received_messages = 0
    sent_messages = 0
    obstacles = None

    def generate_messages(self, balloon, amt):
        for i in range(1, amt):
            self.message_queue[balloon].append("ABCDDEADBEEF")

    def __init__(self, *args, start, end, generic_path):
        self.nodes = []
        self.path = []
        self.path_weight = 0
        self.cg = nx.DiGraph()
        self.reconfigures = []
        self.obstacles = []
        for balloon in args:
            self.nodes.append(balloon)
            self.path.append(balloon)

            self.message_queue[balloon.name] = []
            self.connections[balloon.name] = {}
            
        for tx in self.nodes:
            for rx in self.nodes:
                if tx.name != rx.name:
                    self.connections[tx.name][rx.name] = rx.antenna.sensitivity

        self.start_node = start
        self.end_node = end

        self.generate_messages(self.start_node.name, 100)
        self.generic_path = generic_path
        
        
    def calculate_total_rp(self, time, rp_calculator, path="Generic"):
        total_rp = 0
        pathToUse = self.generic_path
        if path == "Generic":
            pathToUse = self.generic_path
        elif path == "Current":
            pathToUse = self.path
        else:
            raise Exception("Invalid path type")
        
        OutOfSensitivity = False
        for i in range(len(pathToUse)-1):
           tx = pathToUse[i]
           rx = pathToUse[0] if i == len(pathToUse)-1 else pathToUse[i+1]
           
           for i in self.nodes:
               if i.name == tx:
                   tx = i
               if i.name == rx:
                   rx = i
           
           rp = rp_calculator(time, tx, rx)
           total_rp += rp
           if rp < rx.antenna.sensitivity:
               OutOfSensitivity = True
               
        return total_rp, OutOfSensitivity
    
    def data_rate_path(self, time, dr_calculator, path="Generic"):
        pathToUse = self.generic_path
        if path == "Generic":
            pathToUse = self.generic_path
        elif path == "Current":
            pathToUse = self.path
        else:
            raise Exception("Invalid path type")
        
        min_dr = 1e100
        for i in range(len(pathToUse)-1):
           tx = pathToUse[i]
           rx = pathToUse[0] if i == len(pathToUse)-1 else pathToUse[i+1]
           
           for i in self.nodes:
               if i.name == tx:
                   tx = i
               if i.name == rx:
                   rx = i
           
           dr = dr_calculator(time=time, tx=tx, rx=rx, desired_link_margin=self.THRESHHOLD)
           if dr < min_dr:
               min_dr = dr
               
        return min_dr

    def recalculate(self, time, rp_calculator):
        newGraph = nx.DiGraph()
        major_change = False
        for tx in self.nodes:
            for rx in self.nodes:
                if tx == rx:
                    continue
                
                rp_modifier = 0
                dead_node = False

                for obstacle in self.obstacles:
                    if obstacle.otype == ObstacleType.ReceiverPower and rx.name in obstacle.config['appliesTo']:
                        if random.random() < obstacle.config['chance']:
                            rp_modifier = obstacle.config['modifier']
                    elif obstacle.otype == ObstacleType.DeadNode:
                        if obstacle.config['node'].name == rx.name:
                            if random.random() < obstacle.config['chance']:
                                dead_node = True
                        elif obstacle.config['node'].name == tx.name:
                            if random.random() < obstacle.config['chance']:
                                dead_node = True
        
                rp = rp_calculator(time, tx, rx) + rp_modifier

                if rp >= rx.antenna.sensitivity and not dead_node:
                    newGraph.add_edge(tx.name, rx.name, weight=rp)
                    self.connections[tx.name][rx.name] = rp
                else:
                    self.connections[tx.name][rx.name] = False
                
        self.cg = newGraph

    # shortest inclusive path
    def _calculate_si_path(self):
        if not self.cg.has_node(self.start_node.name) or not self.cg.has_node(self.end_node.name):
            # obviously no path
            return [], 0
        simple_paths = list(nx.all_simple_paths(self.cg, source=self.start_node.name, target=self.end_node.name))
            
        for i in range(len(self.nodes), 1, -1):
            filtered_paths = []
            for path in simple_paths:
                if len(path) == i:
                    filtered_paths.append(path)
            
            if len(filtered_paths) == 0:
                continue
                            
            weight_of_paths = [nx.path_weight(self.cg, j, weight='weight') for j in filtered_paths]
            return filtered_paths[weight_of_paths.index(max(weight_of_paths))], max(weight_of_paths)

        return [], 0
        
        
    def transmit(self, time, rp_calculator):
        path, weight = self._calculate_si_path()
        self.path_weight, _ = self.calculate_total_rp(time, rp_calculator, path="Current")
        
        if (weight != 0 and weight > self.path_weight):
            self.reconfigures.append({
                'old': self.path,
                'new': path,
                'time': time,
                'meaningful': weight > self.path_weight + self.THRESHHOLD,
                'old_weight': self.path_weight,
                'new_weight': weight
            })
            
            if weight > self.path_weight + self.THRESHHOLD:
                self.path = path
                self.path_weight = weight
        # elif (weight != self.path_weight and weight != 0 and path != self.path):
        #     self.reconfigures.append({
        #         'old': self.path,
        #         'new': path,
        #         'time': time,
        #         'meaningful': False,
        #         'old_weight': self.path_weight,
        #         'new_weight': weight
        #     })
            
        #     self.path = path
        #     self.path_weight = weight    
        
        copy_queue = copy.deepcopy(self.message_queue)
        for balloon in self.nodes:
            if balloon.name not in path:
                self.stored.append({
                    'time': time,
                    'messages': copy_queue[balloon.name]
                })
            else:
                if len(self.message_queue[balloon.name]) and balloon.name != self.end_node.name == 0:
                    continue
                    
                if balloon.name == self.start_node.name:
                    self.sent_messages += 5
                    
                if balloon.name == self.end_node.name:
                    self.received_messages += len(copy_queue[balloon.name])
                    copy_queue[balloon.name] = copy_queue[balloon.name][5:]
                else:
                    idx_tx = path.index(balloon.name)
                    balloon_rx = 0
                    if idx_tx != len(self.nodes)-1:
                        balloon_rx = idx_tx + 1

                    balloon_rx = path[balloon_rx]

                    copy_queue[balloon.name] = self.message_queue[balloon.name][20:]
                    for i in range(1, 5):
                        copy_queue[balloon_rx].append("ABCDDEADBEEF")
                    self.forwarded += 5

        self.message_queue = copy.deepcopy(copy_queue)
        self.generate_messages(self.start_node.name, 5)

    def add_obstacle(self, Obstacle):
        self.obstacles.append(Obstacle)