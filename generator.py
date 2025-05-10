import random
from typing import List, Tuple, Optional, Any
import traceback  # Import traceback for better error details

# Ensure correct import if SokobanLevel/Pathfinder are in the main directory or adjust path
try:
    # Import specific classes needed
    from SokobanLevel import SokobanLevel, Box, Node
except ImportError:
    print("Error: Cannot import SokobanLevel in generator.py. Check file location/PYTHONPATH.")
    # Define dummy classes to prevent NameErrors if import fails, but logic will break
    class SokobanLevel: pass
    class Box: pass
    class Node: pass

try:
    from pathfinder import Pathfinder
except ImportError:
     print("Error: Cannot import Pathfinder in generator.py. Check file location/PYTHONPATH.")
     class Pathfinder: pass  # Dummy class

# Import utils (assuming it's accessible)
try:
    from utils import *
except ImportError:
     print("Error: Cannot import utils in generator.py. Check file location/PYTHONPATH.")
     # Define dummy functions if needed to prevent NameErrors, though logic will fail
     def copyBoxes(lvl, used): return None
     def check_boundaries(arr, x, y): return False


# --- Updated generatePaths function ---
def generatePaths(lvl: SokobanLevel) -> bool:
    """
    Generates paths between boxes and buttons by removing walls, making the level solvable.
    Args:
        lvl: The SokobanLevel object to modify.
    Returns:
        True if the generation was successful, False otherwise (e.g., timeout, error, impossible).
    """
    steps = 0
    MAX_STEPS = 4000  # Define max steps constant

    # Add a small region check
    small_region = lvl.width * lvl.height < 20
    
    # For very small regions, try a simpler puzzle
    if small_region and len(lvl.targets) > 0:
        # Try a simpler approach for small regions
        result = generate_simple_puzzle(lvl)
        if result:
            return True

    # create ghostBoxes for solving (handle potential copy failure)
    try:
        ghostBoxes = copyBoxes(lvl, False)
        if not ghostBoxes:
            print("Error in generatePaths: Failed to copy boxes (returned None or empty list).")
            lvl.trash = True
            return False
    except Exception as e:
        print(f"Error during copyBoxes: {e}")
        lvl.trash = True
        return False

    # Main loop: append ghostBoxes towards buttons
    while lvl.solveCounter > 0:
        if not ghostBoxes:  # Should not happen if solveCounter > 0, but safety check
            print("Error in generatePaths: No ghostBoxes left but solveCounter > 0.")
            lvl.trash = True
            break

        # --- Calculate Box Paths ---
        try:
            boxPaths = CalcualteBoxPaths(lvl, ghostBoxes)
            # Check if calculation failed for *any* box still needing solving
            if boxPaths is None or len(boxPaths) != len(ghostBoxes) or any(p is None for p in boxPaths):
                print("Error in generatePaths: Failed to calculate one or more required box paths.")
                lvl.trash = True
                break
        except Exception as e:
             print(f"Error during CalcualteBoxPaths: {e}")
             traceback.print_exc()
             lvl.trash = True
             break

        # --- Calculate Player Paths & Choose Best ---
        try:
            playerPathsResult = CalcualtePlayerPaths(lvl, ghostBoxes, boxPaths)
            # Check if finding the best path failed
            if not playerPathsResult or playerPathsResult[1] == -1:
                print("Error in generatePaths: Failed to calculate player paths or find a best path.")
                lvl.trash = True
                break

            allPlayerPaths, bestPathIdx = playerPathsResult
            # Additional checks for valid indices and path data
            if not (0 <= bestPathIdx < len(allPlayerPaths) and
                    0 <= bestPathIdx < len(boxPaths) and
                    allPlayerPaths[bestPathIdx] is not None and  # Check path result exists
                    boxPaths[bestPathIdx] is not None and        # Check path result exists
                    allPlayerPaths[bestPathIdx][0] is not None and  # Check path list exists
                    boxPaths[bestPathIdx][0] is not None):          # Check path list exists
                print(f"Error in generatePaths: Invalid bestPath index {bestPathIdx} or missing path data.")
                lvl.trash = True
                break

            playerPathNodes = allPlayerPaths[bestPathIdx][0]  # List of Nodes for player
            boxPathNodes = boxPaths[bestPathIdx][0]           # List of Nodes for box

            # Check if paths are non-empty (Pathfinder should return at least start node if start=end)
            if not playerPathNodes:
                 print(f"Warning in generatePaths: Player path for bestPath {bestPathIdx} is empty.")
                 # This might indicate player is already at target or pathfinder issue
                 # If player is already there, maybe continue? For now, treat as potential issue.
                 # lvl.trash = True; break
            if not boxPathNodes:
                print(f"Warning in generatePaths: Box path for bestPath {bestPathIdx} is empty.")
                lvl.trash = True; break  # Box cannot reach target

        except Exception as e:
             print(f"Error during CalcualtePlayerPaths or path selection: {e}")
             traceback.print_exc()
             lvl.trash = True
             break

        # --- Remove Walls on Player Path ---
        for node in playerPathNodes:
            # Use row/col indexing for nodes
            try:
                lvl.nodes[node.x][node.y].wall = False  # Assuming node.x=row, node.y=col
                # Check if player path goes through another box's location (shouldn't happen if costs are right)
                if lvl.nodes[node.x][node.y].occupied and \
                   (node.x != lvl.playerX or node.y != lvl.playerY):  # Allow current player pos
                    print(f"Warning in generatePaths: Player path node ({node.x},{node.y}) is occupied.")
                    # lvl.trash = True  # Optional: Flag this as an error
            except IndexError:
                 print(f"Error: Index out of bounds accessing node {node.x},{node.y} during player path wall removal.")
                 lvl.trash = True; break

        if lvl.trash: break  # Check if flagged during player path processing

        # --- Process Box Path & Movement ---
        try:
            thisbox = ghostBoxes[bestPathIdx]
            currentNode = boxPathNodes[0]  # First step target for the box

            # Calculate push direction based on the first step (relative to box's current pos)
            # Assuming node.x = row, node.y = col
            diffX = currentNode.x - thisbox.x  # Change in row index
            diffY = currentNode.y - thisbox.y  # Change in col index

            # Determine how far along the path the box should move (until a turn or end)
            stop = 0  # Index of the last node the box will occupy in this step
            if len(boxPathNodes) > 1:
                for i in range(1, len(boxPathNodes)):
                    nextNode = boxPathNodes[i]
                    # Check if next step continues in the same direction
                    if (diffX == nextNode.x - currentNode.x and diffY == nextNode.y - currentNode.y):
                        currentNode = nextNode  # Advance along straight path
                    else:
                        stop = i - 1  # Stop index is the last node *before* the turn
                        break
                else:  # If loop finished without break, box path is straight
                    stop = len(boxPathNodes) - 1
            # Else: if len is 1, stop remains 0

            # Remove walls along the box's movement path segment
            for i in range(stop + 1):
                if i < len(boxPathNodes):
                    box_path_node = boxPathNodes[i]
                    # Use row/col indexing
                    if 0 <= box_path_node.x < lvl.height and 0 <= box_path_node.y < lvl.width:
                         lvl.nodes[box_path_node.x][box_path_node.y].wall = False
                    else: print(f"Warning: Box path node ({box_path_node.x},{box_path_node.y}) out of bounds.")
                else:
                    print(f"Warning: Index {i} out of bounds accessing boxPath.")
                    lvl.trash = True; break

            if lvl.trash: break  # Check if flagged

            # --- Update Positions ---
            # Player needs to end up where the box *started*, but offset by the push direction
            player_target_x = thisbox.x - diffX  # Target row for player
            player_target_y = thisbox.y - diffY  # Target col for player

            # Box ends up at the 'stop' node's position
            final_box_node = boxPathNodes[stop]
            new_box_x = final_box_node.x  # Target row for box
            new_box_y = final_box_node.y  # Target col for box

            # Clear old occupation (use row/col for node access)
            if 0 <= thisbox.x < lvl.height and 0 <= thisbox.y < lvl.width:
                lvl.nodes[thisbox.x][thisbox.y].occupied = False
            else: print(f"Warning: Old box pos ({thisbox.x},{thisbox.y}) out of bounds.")

            # Update box object's position
            thisbox.setPosition(new_box_x, new_box_y)

            # Set new occupation (use row/col for node access)
            if 0 <= new_box_x < lvl.height and 0 <= new_box_y < lvl.width:
                lvl.nodes[new_box_x][new_box_y].occupied = True
            else:
                print(f"Warning: New box pos ({new_box_x},{new_box_y}) out of bounds.")
                lvl.trash = True; break

            # Update player position AFTER box has moved (use row/col for setPlayerPos)
            lvl.setPlayerPos(player_target_x, player_target_y)

            # --- Check if Box Reached Target ---
            if (new_box_x == thisbox.solveButton.x and new_box_y == thisbox.solveButton.y):
                thisbox.placed = True
                lvl.solveCounter -= 1
                # Remove the corresponding box from ghostBoxes *safely*
                if 0 <= bestPathIdx < len(ghostBoxes):
                    del ghostBoxes[bestPathIdx]
                else:
                    print(f"Error: Invalid index {bestPathIdx} for removing from ghostBoxes.")
                    lvl.trash = True  # This is likely a critical error

        except IndexError as e:
            print(f"Error processing paths/movement (IndexError): {e}")
            traceback.print_exc()
            lvl.trash = True
        except Exception as e:
            print(f"Unexpected error processing paths/movement: {e}")
            traceback.print_exc()
            lvl.trash = True

        # Check trash flag set during this iteration
        if lvl.trash:
            print("Trash flag set during box processing loop.")
            break

        # --- Step Counter & Timeout ---
        steps += 1
        if steps > MAX_STEPS:
            print(f"Warning: generatePaths reached step limit ({MAX_STEPS}).")
            lvl.trash = True
            break

    # --- Cleanup and Return ---
    # Reset player position AFTER loop finishes or breaks
    try:
        lvl.setPlayerPos(lvl.playerstartX, lvl.playerstartY)
    except AttributeError:
        print("Warning: Could not reset player position (playerstartX/Y missing?).")
        # This might happen if object placement failed earlier
        lvl.trash = True  # Flag as error if reset fails

    # Final return value based on trash flag
    return not lvl.trash

def generate_simple_puzzle(lvl):
    """Simple puzzle generator for small regions"""
    # Return early if no targets or if the level is marked invalid
    if not lvl.targets or getattr(lvl, "trash", False):
        return False
        
    # Just place one box near a target if possible
    if lvl.boxes:
        box = lvl.boxes[0]
        target = lvl.targets[0]
        
        # Try to place the box one square away from the target
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = target.x + dx, target.y + dy
            
            # Check if valid position
            if (0 <= nx < lvl.width and 0 <= ny < lvl.height and
                not lvl.nodes[ny][nx].wall):
                box.placeExactly(nx, ny)
                return True
                
    return False


# --- Updated Helper Functions (with error checking) ---
def copyBoxes(lvl: SokobanLevel, used: bool) -> Optional[List[Box]]:
    """Copies boxes from the level, returns list or None on error."""
    newBoxes = []
    if not hasattr(lvl, 'boxes') or not hasattr(lvl, 'nodes'):
         print("Error in copyBoxes: lvl object missing 'boxes' or 'nodes'.")
         return None
    # Check if lvl dimensions are valid
    if not hasattr(lvl, 'height') or not hasattr(lvl, 'width') or lvl.height <= 0 or lvl.width <= 0:
         print("Error in copyBoxes: lvl object has invalid dimensions.")
         return None

    for i in range(len(lvl.boxes)):
        box = lvl.boxes[i]
        if not isinstance(box, Box) or not hasattr(box, 'x') or not hasattr(box, 'y') or not hasattr(box, 'solveButton'):
             print(f"Error in copyBoxes: Box {i} is invalid or missing attributes.")
             return None  # Treat invalid box data as critical error

        newBoxes.append(Box(box.x, box.y, box.solveButton))
        # Use consistent row/col indexing for nodes
        if 0 <= box.x < lvl.height and 0 <= box.y < lvl.width:
             lvl.nodes[box.x][box.y].occupied = True
             lvl.nodes[box.x][box.y].used = used
        else:
             print(f"Warning in copyBoxes: Box position ({box.x},{box.y}) out of level bounds ({lvl.height}x{lvl.width}).")
             # Decide if this is critical - for now, allow copy but node state won't be set
    return newBoxes


def CalcualteBoxPaths(lvl: SokobanLevel, ghostBoxes: List[Box]) -> Optional[List[Optional[tuple]]]:
    """Calculates paths for boxes, returns list of path results (or None) or None on critical error."""
    boxPaths = []
    if not hasattr(lvl, 'nodes'):
        print("Error in CalcualteBoxPaths: lvl object missing 'nodes'.")
        return None
    if not hasattr(lvl, 'height') or not hasattr(lvl, 'width') or lvl.height <= 0 or lvl.width <= 0:
         print("Error in CalcualteBoxPaths: lvl object has invalid dimensions.")
         return None

    for i in range(len(ghostBoxes)):
        thisbox = ghostBoxes[i]
        if not isinstance(thisbox, Box) or not hasattr(thisbox, 'x') or not hasattr(thisbox, 'y') or not hasattr(thisbox, 'solveButton'):
            print(f"Error in CalcualteBoxPaths: ghostBox {i} is invalid.")
            return None  # Treat as critical

        # Use row/col indexing for nodes
        if 0 <= thisbox.x < lvl.height and 0 <= thisbox.y < lvl.width:
            try:
                lvl.nodes[thisbox.x][thisbox.y].occupied = False  # Allow pathfinding through start pos
                solver = Pathfinder(lvl, thisbox.x, thisbox.y, thisbox.solveButton.x, thisbox.solveButton.y)
                path_result = solver.returnPath(True)  # isBox = True
                lvl.nodes[thisbox.x][thisbox.y].occupied = True  # Restore occupation state

                # Check if pathfinder returned valid data (list of nodes, cost)
                if path_result and isinstance(path_result, tuple) and len(path_result) == 2 and path_result[0] is not None:
                    boxPaths.append(path_result)
                else:
                    print(f"Warning: Pathfinder failed to find a box path for box {i} from ({thisbox.x},{thisbox.y}) to target ({thisbox.solveButton.x},{thisbox.solveButton.y}).")
                    boxPaths.append(None)  # Append None for failure
            except IndexError:
                 print(f"Error in CalcualteBoxPaths: Index out of bounds accessing node for box {i} at ({thisbox.x},{thisbox.y}).")
                 lvl.nodes[thisbox.x][thisbox.y].occupied = True  # Try to restore state
                 return None  # Critical error
            except Exception as e:
                 print(f"Error during Pathfinder for box {i}: {e}")
                 traceback.print_exc()
                 lvl.nodes[thisbox.x][thisbox.y].occupied = True  # Try to restore state
                 return None  # Critical error
        else:
            print(f"Warning in CalcualteBoxPaths: Box position ({thisbox.x},{thisbox.y}) out of bounds.")
            boxPaths.append(None)  # Indicate failure for this box

    # Check if the number of results matches the number of boxes
    if len(boxPaths) != len(ghostBoxes):
        print("Error in CalcualteBoxPaths: Mismatch between number of results and ghostBoxes.")
        return None

    return boxPaths


def CalcualtePlayerPaths(lvl: SokobanLevel, ghostBoxes: List[Box], boxPaths: list) -> Optional[Tuple[List[Optional[tuple]], int]]:
    """Calculates player paths, returns list of results and best path index, or None on critical error."""
    playerPaths = []
    bestPathIdx = -1
    lowestCost = float('inf')

    if not hasattr(lvl, 'nodes'): print("Error in CalcualtePlayerPaths: lvl missing nodes."); return None
    if not hasattr(lvl, 'height') or not hasattr(lvl, 'width'): print("Error in CalcualtePlayerPaths: lvl missing dimensions."); return None
    if boxPaths is None or len(ghostBoxes) != len(boxPaths): print("Error in CalcualtePlayerPaths: Mismatch or missing boxPaths."); return None

    for i in range(len(ghostBoxes)):
        thisbox = ghostBoxes[i]
        if boxPaths[i] is None or not boxPaths[i][0]:  # Check if box path failed or is empty
             playerPaths.append(None)
             continue  # Skip player path calc if box path is unusable

        first_box_step_node = boxPaths[i][0][0]
        if not isinstance(first_box_step_node, Node):
             print(f"Error: Invalid first step node type for box {i}"); return None

        # Determine player target position behind the box (using row/col logic)
        player_target_x = thisbox.x  # Target Row
        player_target_y = thisbox.y  # Target Col
        # Check direction of first box step
        if first_box_step_node.x == thisbox.x + 1: player_target_x -= 1  # Box moves South(row+1), player starts North(row-1)
        elif first_box_step_node.x == thisbox.x - 1: player_target_x += 1  # Box moves North(row-1), player starts South(row+1)
        elif first_box_step_node.y == thisbox.y + 1: player_target_y -= 1  # Box moves East(col+1), player starts West(col-1)
        elif first_box_step_node.y == thisbox.y - 1: player_target_y += 1  # Box moves West(col-1), player starts East(col+1)
        else:
             print(f"Warning: Cannot determine player push position for box {i}. Step node ({first_box_step_node.x},{first_box_step_node.y}), box ({thisbox.x},{thisbox.y}).")
             playerPaths.append(None); continue

        # Check bounds before calling pathfinder and accessing nodes
        if not (0 <= lvl.playerX < lvl.height and 0 <= lvl.playerY < lvl.width):
             print(f"Warning: Player start ({lvl.playerX},{lvl.playerY}) out of bounds."); playerPaths.append(None); continue
        if not (0 <= player_target_x < lvl.height and 0 <= player_target_y < lvl.width):
             print(f"Warning: Player target ({player_target_x},{player_target_y}) out of bounds."); playerPaths.append(None); continue

        original_occupied_state = False
        try:
            # Make box location temporarily non-occupied for player pathfinding
            if 0 <= thisbox.x < lvl.height and 0 <= thisbox.y < lvl.width:
                 original_occupied_state = lvl.nodes[thisbox.x][thisbox.y].occupied
                 lvl.nodes[thisbox.x][thisbox.y].occupied = False
            else: pass  # Already warned if box out of bounds

            # Calculate player path
            solver = Pathfinder(lvl, lvl.playerX, lvl.playerY, player_target_x, player_target_y)
            path_result = solver.returnPath(False)  # isBox = False

            # Restore box occupation state
            if 0 <= thisbox.x < lvl.height and 0 <= thisbox.y < lvl.width:
                 lvl.nodes[thisbox.x][thisbox.y].occupied = original_occupied_state

            # Process path result
            if path_result and isinstance(path_result, tuple) and len(path_result) == 2 and path_result[0] is not None:
                playerPaths.append(path_result)
                currentCost = path_result[1]
                if currentCost < lowestCost:
                    lowestCost = currentCost
                    bestPathIdx = i
            else:
                # print(f"Warning: Pathfinder failed player path for box {i}.")  # Can be noisy
                playerPaths.append(None)

        except IndexError:
             print(f"Error: Index out of bounds during player path calc for box {i}.")
             # Restore occupation state if possible
             if 0 <= thisbox.x < lvl.height and 0 <= thisbox.y < lvl.width: lvl.nodes[thisbox.x][thisbox.y].occupied = original_occupied_state
             return None  # Critical error
        except Exception as e:
             print(f"Error during Pathfinder for player path (box {i}): {e}")
             traceback.print_exc()
             if 0 <= thisbox.x < lvl.height and 0 <= thisbox.y < lvl.width: lvl.nodes[thisbox.x][thisbox.y].occupied = original_occupied_state
             return None  # Critical error

    # Final check for best path index validity
    if len(playerPaths) != len(ghostBoxes):
         print("Error: Mismatch between playerPaths results and ghostBoxes.")
         return None

    if bestPathIdx == -1 and any(p is not None for p in playerPaths):
         # Fallback: if no path was strictly 'best' (all failed or had infinite cost?), pick the first valid one found
         first_valid = next((idx for idx, p in enumerate(playerPaths) if p is not None), -1)
         print(f"Warning: No path found with finite cost. Falling back to first valid path index: {first_valid}")
         bestPathIdx = first_valid

    return (playerPaths, bestPathIdx)

def check_region_viability(lvl):
    """Check if a region has enough space for a valid puzzle"""
    open_count = sum(1 for row in lvl.nodes for node in row if not node.wall)
    
    # Need minimum viable space
    if open_count < 4:
        return False
        
    # Check if there's at least one 2x2 open area somewhere
    has_open_area = False
    for y in range(lvl.height - 1):
        for x in range(lvl.width - 1):
            if (not lvl.nodes[y][x].wall and
                not lvl.nodes[y][x+1].wall and
                not lvl.nodes[y+1][x].wall and
                not lvl.nodes[y+1][x+1].wall):
                has_open_area = True
                break
                
    return has_open_area
