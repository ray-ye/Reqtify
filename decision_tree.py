"""This module creates the decision tree used to filter songs."""
import csv
from typing import Any, Optional


class DecisionTree:
    """A Decision Tree that filters songs

    Instance Attributes:
    - _root: the roots of tree:
    - _subtrees: a list of all subtrees
    """
    _root: Optional[Any]
    _subtrees: list['DecisionTree']

    def __init__(self, root: Any, subtrees: list) -> None:
        """Initialize a new decision tree."""
        self._root = root
        self._subtrees = subtrees
        # pythonTA complaining changed from [] to subtrees

    def is_empty(self) -> bool:
        """Return whether this tree is empty.

        >>> t1 = DecisionTree(None, [])
        >>> t1.is_empty()
        True
        >>> t2 = DecisionTree(3, [])
        >>> t2.is_empty()
        False
        """
        return self._root is None

    def __len__(self) -> int:
        """Return the number of items contained in this tree.

        >>> t1 = DecisionTree(None, [])
        >>> len(t1)
        0
        >>> t2 = DecisionTree(3, [DecisionTree(4, []), DecisionTree(1, [])])
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

        >>> t = DecisionTree(1, [DecisionTree(2, []), DecisionTree(5, [])])
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
        cursor = self
        for item in items:
            for subtree in cursor._subtrees:
                if subtree._root == item:
                    cursor = subtree
                    break
            else:
                cursor._subtrees.append(DecisionTree(item, []))
                cursor = cursor._subtrees[-1]

    def children(self, path: list[bool]) -> list[str]:
        """Return the children of this tree that match the given path."""
        cursor = self
        for item in path:
            for subtree in cursor._subtrees:
                if subtree._root == item:
                    cursor = subtree
                    break
            else:
                return []

        return [str(sbt._root) for sbt in cursor._subtrees]

    def build_tree(self, file_path: str) -> None:
        """Build a decision tree from the given data."""

        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            data = [list(map(lambda x: x == 'True', rw[1:])) + [rw[0]] for rw in reader]

        for row in data:
            self.insert_sequence(row)


if __name__ == '__main__':
    tree = DecisionTree(None, [])
    tree.build_tree('songs.csv')
    print(len(tree.children([True, False, False, False, True, True, False, True, False, False])))

    for i in tree.children([True, False, False, False, True, True, False, True, False, False]):
        print('spotify:track:' + i)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
