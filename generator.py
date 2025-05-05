import random
from utils import *
from typing import List, Tuple, Optional, Any
from SokobanLevelGenerator import *
from pathfinder import *

#  generates the paths between boxes and buttons in a level by removing walls

def generatePaths(lvl):
    steps = 0
    # create ghostBoxes for solving
    ghostBoxes = copyBoxes(lvl, False)
    # append the ghostBoxes towards the buttons
    while (lvl.solveCounter > 0):
        # calculate the paths from all boxes to their buttons
        boxPaths = CalcualteBoxPaths(lvl, ghostBoxes)

        # calculate the player paths to all boxes and choose the lowest cost path
        playerPaths = CalcualtePlayerPaths(lvl, ghostBoxes, boxPaths)
        bestPath = playerPaths[1]
        playerPath = playerPaths[0][bestPath][0]
        boxPath = boxPaths[bestPath][0]

        # remove all walls on the player's path
        for i in range(len(playerPath)):
            if not playerPath[i].permanent:
                playerPath[i].wall = False
                if playerPath[i].occupied:
                    lvl.trash = True

        # append the box into the solving direction
        thisbox = ghostBoxes[bestPath]
        currentNode = boxPath[0]
        diffX = currentNode.x - thisbox.x
        diffY = currentNode.y - thisbox.y
        stop = 0

        # if the box-path is longer than 1, append until there is a turn
        if (len(boxPath) > 1):
            for i in range(1, len(boxPath)):
                nextNode = boxPath[i]
                if (diffX == nextNode.x - currentNode.x and diffY == nextNode.y - currentNode.y):
                    currentNode = nextNode
                else:
                    stop = i - 1
                    break
                    
        # remove all walls on the box's path
        for i in range(stop+1):
            if not boxPath[i].permanent:
                boxPath[i].wall = False

        # set new player and box positions
        lvl.nodes[thisbox.x][thisbox.y].occupied = False
        thisbox.setPosition(boxPath[stop].x, boxPath[stop].y)
        lvl.nodes[thisbox.x][thisbox.y].occupied = True
        lvl.setPlayerPos(thisbox.x - diffX, thisbox.y - diffY)

        # check if the moved box is on the button
        if (thisbox.x == thisbox.solveButton.x and thisbox.y == thisbox.solveButton.y):
            thisbox.placed = True
            lvl.solveCounter -= 1
            del ghostBoxes[bestPath]

        steps += 1
        if (steps > 4000):
            lvl.trash = True
            break
            
    # reset player position
    lvl.setPlayerPos(lvl.playerstartX, lvl.playerstartY)
    px = lvl.playerX
    py = lvl.playerY


def copyBoxes(lvl, used):
    newBoxes = []
    for i in range(len(lvl.boxes)):
        newBoxes.append(Box(lvl.boxes[i].x, lvl.boxes[i].y, lvl.boxes[i].solveButton))
        lvl.nodes[lvl.boxes[i].x][lvl.boxes[i].y].occupied = True
        lvl.nodes[lvl.boxes[i].x][lvl.boxes[i].y].used = used
        
    return newBoxes


# calculate all boxpaths and return them in an array
def CalcualteBoxPaths(lvl, ghostBoxes):
    boxPaths = []
    for i in range(len(ghostBoxes)):
        thisbox = ghostBoxes[i]
        lvl.nodes[thisbox.x][thisbox.y].occupied = False
        solver = Pathfinder(lvl, thisbox.x, thisbox.y, thisbox.solveButton.x, thisbox.solveButton.y)
        boxPaths.append(solver.returnPath(True))
        lvl.nodes[thisbox.x][thisbox.y].occupied = True
    return boxPaths


# return all player paths and the index of the lowest cost one
def CalcualtePlayerPaths(lvl, ghostBoxes, boxPaths):
    playerPaths = []
    bestPath = -1
    lowestCost = 100000000
    for i in range(len(ghostBoxes)):
        newX = ghostBoxes[i].x
        newY = ghostBoxes[i].y
        if (boxPaths[i][0][0].x == ghostBoxes[i].x + 1):
            newX -= 1
        elif (boxPaths[i][0][0].x == ghostBoxes[i].x - 1):
            newX += 1
        elif (boxPaths[i][0][0].y == ghostBoxes[i].y + 1):
            newY -= 1
        else:
            newY += 1
        solver = Pathfinder(lvl, lvl.playerX, lvl.playerY, newX, newY)
        playerPaths.append(solver.returnPath(False))
        if (playerPaths[i][1] < lowestCost):
            lowestCost = playerPaths[i][1]
            bestPath = i
    return ([playerPaths, bestPath])

