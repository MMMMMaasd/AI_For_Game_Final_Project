import random
from typing import List, Tuple, Optional, Any
from SokobanLevel import Node, SokobanLevel

# binary search in sorted array
def binarySearch(array, element, compare_func):
    low = 0
    high = len(array) - 1
    while low <= high:
        mid = (low + high) // 2
        cmp = compare_func(element, array[mid])
        if cmp > 0:
            low = mid + 1
        elif cmp < 0:
            high = mid - 1
        else:
            return mid
    return -(low + 1)
    
def add_to_sorted_array(array, element, compare_func) -> None:
    index = binarySearch(array, element, compare_func)
    if index < 0:
        index = -index - 1
    array.insert(index, element)

def f_comparer(a: Node, b: Node) -> int:
    return a.f - b.f
    
def check_boundaries(array2D, x: int, y: int) -> bool:
        return 0 <= x < len(array2D) and 0 <= y < len(array2D[0])


def surrounded(lvl, x, y):
    for i in range(x-1, x+2):
        for j in range(y-1, y+2):
            if (check_boundaries(lvl.nodes, i, j) and not lvl.nodes[i][j].wall):
                return False
    return True
