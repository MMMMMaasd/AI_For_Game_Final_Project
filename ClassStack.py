# ClassStack.py
# Simple stack implementation (no changes needed)

class Stack:
    """A basic stack implementation using a Python list."""
    def __init__(self):
        """Initializes an empty stack."""
        self.items = []

    def is_empty(self):
        """Checks if the stack is empty."""
        return len(self.items) == 0

    def push(self, item):
        """Adds an item to the top of the stack."""
        self.items.append(item)

    def pop(self):
        """Removes and returns the item from the top of the stack."""
        if not self.is_empty():
            return self.items.pop()
        else:
            raise IndexError("pop from empty stack")

    def size(self):
        """Returns the number of items in the stack."""
        return len(self.items)

    def peek(self):
        """Returns the top item without removing it."""
        if not self.is_empty():
            return self.items[-1]
        else:
            raise IndexError("peek from empty stack")

