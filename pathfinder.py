import random
from utils import *
from typing import List, Tuple, Optional, Any
from SokobanLevelGenerator import Node, SokobanLevel

# Pathfinder Constants (same as JavaScript)
WALL_COST = 100
PATH_COST = 1
PLAYER_PATH_COST = -1
BOX_COST = 10000

class Pathfinder:
    def __init__(self, Level: SokobanLevel, startX: int, startY: int, endX: int, endY: int):
        self.level = Level
        self.nodes = self.level.nodes
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY
        self.open = []
        self.closed = []
    
    # return path and cost, cost of player-path and box-path can differ
    def returnPath(self, isBox):
        self.open.append(self.nodes[self.startX][self.startY])
        while self.open:
            current_node = self.open.pop(0)
            if(current_node.x == self.endX and current_node.y == self.endY):
                self.open.append(current_node)
                return self.sumPath(current_node)
            else:
                current_node.closed = True
                self.closed.append(current_node)
                self.checkNeighbor(current_node.x + 1, current_node.y, current_node, isBox)
                self.checkNeighbor(current_node.x - 1, current_node.y, current_node, isBox)
                self.checkNeighbor(current_node.x, current_node.y + 1, current_node, isBox)
                self.checkNeighbor(current_node.x, current_node.y - 1, current_node, isBox)
        print("no path found")
        return self.sumPath(current_node)
    
    def sumPath(self, endNode):
        path = []
        cost = endNode.cost
        while(endNode.parent is not None):
            path.insert(0, endNode)
            endNode = endNode.parent
        self.resetNodes()
        return (path, cost)
        
    
    def checkNeighbor(self, x, y, parent, isBox):
        if (check_boundaries(self.nodes, x, y)):
            thisNode = self.nodes[x][y]
            if (not thisNode.closed and not thisNode.checked):
                thisNode.cost = self.calculateCost(thisNode, parent, isBox)
                thisNode.f = thisNode.cost + abs(x - self.endX) + abs(y - self.endY)
                thisNode.parent = parent
                thisNode.checked = True
                add_to_sorted_array(self.open, thisNode, f_comparer)
            elif (not thisNode.closed):
                cost = self.calculateCost(thisNode, parent, isBox);
                if (cost < thisNode.cost and thisNode.parent.parent):
                    thisNode.cost = cost
                    thisNode.f = thisNode.cost + abs(x - self.endX) + abs(y - self.endY)
                    thisNode.parent = parent

    
    #calculate the cost of a position
    def nodeCost(self, x, y):
        if (check_boundaries(self.nodes, x, y)):
            node = self.nodes[x][y];
            if node.permanent:  # Treat permanent walls as impassable
                return PLAYER_PATH_COST
            if (node.occupied):
                return BOX_COST
            else:
                return WALL_COST if node.wall else PLAYER_PATH_COST
        else:
            return BOX_COST

    # reset the level's nodes for further pathfinding
    def resetNodes(self):
        for node in self.open + self.closed:
            node.checked = False
            node.closed = False
            node.parent = None
            node.cost = 0
        self.open = []
        self.closed = []
            
    # calculate the cost for a  node
    def calculateCost(self, node, parent, isBox):
        tempCost = 0
        if (node.occupied):
            tempCost = parent.cost + BOX_COST
        else:
            if isBox:
                temp_cost = parent.cost + (WALL_COST if node.wall else PATH_COST)
            else:
                temp_cost = parent.cost + (WALL_COST if node.wall else PLAYER_PATH_COST)
                
        if (isBox and parent.parent):
            cost1 = 0
            cost2 = 0

            if (node.x - 1 == parent.x and node.x - 2 != parent.parent.x):
                # case 1: node is right of parent
                if (node.y - 1 == parent.parent.y):
                    # case 1.1: node is up right of parent.parent
                    cost1 = self.nodeCost(node.x - 2, node.y) + self.nodeCost(node.x - 2, node.y - 1)
                    cost2 = self.nodeCost(node.x, node.y - 1) + self.nodeCost(node.x, node.y + 1) + self.nodeCost(node.x - 1, node.y + 1) + self.nodeCost(node.x - 2, node.y + 1) + self.nodeCost(node.x - 2, node.y)
                else:
                    # case 1.2: node is down right of parent.parent
                    cost1 = self.nodeCost(node.x - 2, node.y) + self.nodeCost(node.x - 2, node.y + 1)
                    cost2 = self.nodeCost(node.x, node.y - 1) + self.nodeCost(node.x, node.y + 1) + self.nodeCost(node.x - 1, node.y - 1) + self.nodeCost(node.x - 2, node.y - 1) + self.nodeCost(node.x - 2, node.y)
            elif (node.x + 1 == parent.x and node.x + 2 != parent.parent.x):
                # case 2: node is left of parent
                if (node.y - 1 == parent.parent.y):
                    # case 2.1: node is up left of parent.parent
                    cost1 = self.nodeCost(node.x + 2, node.y) + self.nodeCost(node.x + 2, node.y - 1)
                    cost2 = self.nodeCost(node.x, node.y - 1) + self.nodeCost(node.x, node.y + 1) + self.nodeCost(node.x + 1, node.y + 1) + self.nodeCost(node.x + 2, node.y + 1) + self.nodeCost(node.x + 2, node.y)
                else:
                    # case 2.2: node is down left of parent.parent
                    cost1 = self.nodeCost(node.x + 2, node.y) + self.nodeCost(node.x + 2, node.y + 1)
                    cost2 = self.nodeCost(node.x, node.y - 1) + self.nodeCost(node.x, node.y + 1) + self.nodeCost(node.x + 1, node.y - 1) + self.nodeCost(node.x + 2, node.y - 1) + self.nodeCost(node.x + 2, node.y)
            elif (node.y - 1 == parent.y and node.y - 2 != parent.parent.y):
                # case 3: node is above parent
                if (node.x - 1 == parent.parent.x):
                    # case 3.1: node is right up of parent.parent
                    cost1 = self.nodeCost(node.x, node.y - 2) + self.nodeCost(node.x - 1, node.y - 2)
                    cost2 = self.nodeCost(node.x - 1, node.y) + self.nodeCost(node.x + 1, node.y) + self.nodeCost(node.x + 1, node.y - 1) + self.nodeCost(node.x + 1, node.y - 2) + self.nodeCost(node.x, node.y - 2)
                else:
                    # case 3.2: node is left up of parent.parent
                    cost1 = self.nodeCost(node.x, node.y - 2) + self.nodeCost(node.x + 1, node.y - 2)
                    cost2 = self.nodeCost(node.x - 1, node.y) + self.nodeCost(node.x + 1, node.y) + self.nodeCost(node.x - 1, node.y - 1) + self.nodeCost(node.x - 1, node.y - 2) + self.nodeCost(node.x, node.y - 2)
            elif (node.y + 1 == parent.y and node.y + 2 != parent.parent.y):
                # case 4: node is under parent
                if (node.x - 1 == parent.parent.x):
                    # case 4.1: node is right down of parent.parent
                    cost1 = self.nodeCost(node.x, node.y + 2) + self.nodeCost(node.x - 1, node.y + 2)
                    cost2 = self.nodeCost(node.x - 1, node.y) + self.nodeCost(node.x + 1, node.y) + self.nodeCost(node.x + 1, node.y + 1) + self.nodeCost(node.x + 1, node.y + 2) + self.nodeCost(node.x, node.y + 2)
                else:
                    # case 4.2: node is left down of parent.parent
                    cost1 = self.nodeCost(node.x, node.y + 2) + self.nodeCost(node.x + 1, node.y + 2)
                    cost2 = self.nodeCost(node.x - 1, node.y) + self.nodeCost(node.x + 1, node.y) + self.nodeCost(node.x - 1, node.y + 1) + self.nodeCost(node.x - 1, node.y + 2) + self.nodeCost(node.x, node.y + 2)
                        
            tempCost += (cost1 if cost1 < cost2 else cost2)
            
        elif (isBox):
            if (node.x - 1 == parent.x):
                tempCost += self.nodeCost(node.x - 2, node.y)
            elif (node.x + 1 == parent.x):
                tempCost += self.nodeCost(node.x + 2, node.y)
            elif (node.y - 1 == parent.y):
                tempCost += self.nodeCost(node.x, node.y - 2)
            elif (node.y + 1 == parent.y):
                tempCost += self.nodeCost(node.x, node.y + 2)

        # for optimizing prefer used nodes
        if (node.used):
            tempCost -= 5;
        return tempCost


#lvl = SokobanLevel(20, 20, 3)
#print(lvl.get_tile_grid())
#solver = Pathfinder(lvl, lvl.boxes[0].x, lvl.boxes[0].y, lvl.boxes[0].solveButton.x, lvl.boxes[0].solveButton.y)
#print(solver.returnPath(True))
