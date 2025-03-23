import csv
from typing import Any, Optional


class DecisionTree:
    _root: Optional[Any]
    _subtrees: list['DecisionTree']

    def __init__(self, root: Optional[Any], subtrees: list['DecisionTree']) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

        Preconditions:
            - root is not none or subtrees == []
        """
        self._root = root
        self._subtrees = subtrees

    def is_empty(self) -> bool:
        """Return whether this tree is empty.

        >>> t1 = Tree(None, [])
        >>> t1.is_empty()
        True
        >>> t2 = Tree(3, [])
        >>> t2.is_empty()
        False
        """
        return self._root is None

    def __len__(self) -> int:
        """Return the number of items contained in this tree.

        >>> t1 = Tree(None, [])
        >>> len(t1)
        0
        >>> t2 = Tree(3, [Tree(4, []), Tree(1, [])])
        >>> len(t2)
        3
        """
        if self.is_empty():
            return 0
        else:
            size = 1  # count the root
            for subtree in self._subtrees:
                size += subtree.__len__()  # could also write len(subtree)
            return size

    def __contains__(self, item: Any) -> bool:
        """Return whether the given is in this tree.

        >>> t = Tree(1, [Tree(2, []), Tree(5, [])])
        >>> t.__contains__(1)
        True
        >>> t.__contains__(5)
        True
        >>> t.__contains__(4)
        False
        """
        if self.is_empty():
            return False
        elif self._root == item:
            return True
        else:
            for subtree in self._subtrees:
                if subtree.__contains__(item):
                    return True
            return False
    
    def insert_sequence(self, items: list) -> None:
        """Insert the given sequence of items into this tree."""
        if not items:
            return

        idx = None
        for i, subtree in enumerate(self._subtrees):
            if subtree._root == items[0]:
                idx = i
                break

        if idx is None:
            self._subtrees.append(DecisionTree(items[0], []))
            idx = len(self._subtrees) - 1

        self._subtrees[idx].insert_sequence(items[1:])

        # TODO: CHANGE THIS TO A NON RECURSIVE IMPLEMENTATION LATER FOR EFFICIENCY

    def children(self, path: list[bool]) -> list[str]:
        """Return the children of this tree that match the given path."""

        if not path:
            res = []
            for subtree in self._subtrees:
                res.append(subtree._root)
            return res

        # TODO: CHANGE THIS TO A NON RECURSIVE IMPLEMENTATION LATER FOR EFFICIENCY
        for subtree in self._subtrees:
            if subtree._root == path[0]:
                return subtree.children(path[1:])

        return []

    def build_tree(self, data: list[list]) -> None:
        """Build a decision tree from the given data."""
        for row in data:
            self.insert_sequence(row)
    
# test the tree
tree = DecisionTree(None, [])
with open('songs.csv', 'r') as file:
    reader = csv.reader(file)
    data = [list(map(lambda x: x=='True', row[1:])) + [row[0]] for row in reader]
tree.build_tree(data)
print(len(tree.children([True,False,False,False,True,True,False,True,False,False])))

for i in tree.children([True,False,False,False,True,True,False,True,False,False]):
    print('spotify:track:' + i)