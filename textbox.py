import pygame_gui
import pygame

class TextBox():
    def __init__(self, position, dimension, manager, object_id, center):
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
        return pygame_gui.elements.UITextEntryLine(
            relative_rect=self.rect,
            manager=self.manager,
            object_id=self.object_id
        )

    def get_pos(self) -> tuple:
        return self.x_pos, self.y_pos

    def top_left(self) -> tuple:
        return self.rect.topleft

    def get_id(self):
        return self.object_id

    def get_dimensions(self):
        return self.width, self.height

    def change_pos(self, x, y):
        self.rect.centerx += x
        self.rect.centery += y

    def set_pos(self, position):
        self.rect.x = position[0]
        self.rect.y = position[1]

