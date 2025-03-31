"""This module is for creating text boxes"""
import pygame_gui
import pygame


class TextBox:
    """Creates text boxes

    Instance Attributes:
    - x_pos: position of x
    - y_pos: position of y
    - width: width of text box
    - height: height of textbox
    - manager: manager
    - object_id: id of object
    - rect: rectangle
    """
    x_pos: float
    y_pos: float
    width: float
    height: float
    manager: any
    object_id: str
    rect: any

    def __init__(self, position: tuple, dimension: tuple, manager: any, object_id: any, center: any) -> None:
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.width = dimension[0]
        self.height = dimension[1]
        self.manager = manager
        self.object_id = object_id
        self.rect = pygame.Rect((0, 0), (self.width, self.height))
        if center:
            self.rect.center = (self.x_pos, self.y_pos)
        else:
            self.rect.topleft = (self.x_pos, self.y_pos)

    def get_result(self) -> pygame_gui.elements.UITextEntryLine:
        """Returns results"""
        return pygame_gui.elements.UITextEntryLine(
            relative_rect=self.rect,
            manager=self.manager,
            object_id=self.object_id
        )

    def get_pos(self) -> tuple:
        """Returns position"""
        return self.x_pos, self.y_pos

    def top_left(self) -> tuple:
        """Returns top left of rectangle"""
        return self.rect.topleft

    def get_id(self) -> any:
        """Returns id"""
        return self.object_id

    def get_dimensions(self) -> tuple:
        """Returns dimension"""
        return self.width, self.height

    def change_pos(self, x: float, y: float) -> None:
        """Changes position"""
        self.rect.centerx += x
        self.rect.centery += y

    def set_pos(self, position: tuple) -> None:
        """Sets position"""
        self.rect.x = position[0]
        self.rect.y = position[1]


if __name__ == '__main__':

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
