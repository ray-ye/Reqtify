"""This module generates the forms that will be used"""
import pygame
from textbox import TextBox
from button import Button


class Form():
    """Form that generates a form used to fill up information
    
    Instance Attributes:
    - x_pos: position of x
    - y_pos: position of y
    - ui_manager: manages ui
    - rect: creates a rectange
    - prompter: prompter that takes in dict
    - margin: margin of 120 pixels
    - padding: padding of 70 pixels
    - button: a pressable button
    - background_colour: background colour
    - font_size: size of the font
    - font: font type
    - error: if there is error
    """
    x_pos: tuple
    y_pos: tuple
    ui_manager: any
    rect: any
    prompter: dict
    margin: int
    padding: int
    button: Button
    background_colour: tuple
    font_size: any
    font: any
    error: bool

    def __init__(
            self, position: tuple, manager: any, button_text: str, background_colour: tuple, font: any, font_size: int
    ) -> None:
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.ui_manager = manager
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.prompter = {}
        self.margin = 120
        self.padding = 70
        self.button = Button(None,
                             position,
                             (200, 60),
                             button_text,
                             "Arial",
                             35,
                             (30, 30, 30),
                             (112, 191, 119),
                             35)
        self.background_colour = background_colour
        self.font_size = font_size
        self.font = pygame.font.SysFont(font, font_size)
        self.error = False

    def add_textbox(self, title: any, width: float) -> None:
        """Adds text box"""
        self.rect.width = 300

        if len(self.prompter) > 1:
            for prompter in self.get_prompters():
                prompter.change_pos(0, -50)
            self.rect.height += 100
        else:
            self.rect.height += 175

        self.rect.center = (self.x_pos, self.y_pos)
        self.button.set_pos(self.x_pos, self.y_pos + self.rect.height / 2 - self.padding)

        if self.prompter:
            position = self.rect.center[0], list(self.get_prompters())[-1].rect.topleft[1] + self.margin

        else:
            position = self.rect.center[0], self.rect.centery - self.rect.height / 2

        self.prompter[title] = TextBox(position, (width, 45), self.ui_manager, "#" + title.lower().replace(" ", ""),
                                       True)

    def draw(self, screen: any) -> None:
        """Draws"""
        counter = 1
        pygame.draw.rect(screen, self.background_colour, self.rect, border_radius=30)
        self.button.draw(screen)
        for prompter in self.prompter:
            textbox = self.prompter[prompter]
            text = self.font.render(prompter, True, (30, 30, 30))
            screen.blit(text, (textbox.rect.topleft[0], textbox.rect.topleft[1] - 25))
            counter += 1

    def get_prompters(self) -> any:
        """Returns prompt"""
        return self.prompter.values()

    def error_message(self, message: str, screen: any) -> None:
        """Displays error message"""
        font = pygame.font.SysFont("Arial", 9)
        text = font.render(message, True, (144, 8, 8))
        text_rect = text.get_rect(center=(self.rect.centerx, list(self.get_prompters())[-1].rect.bottomleft[1] + 20))
        screen.blit(text, text_rect)

    def check_error(self) -> any:
        """Returns error"""
        return self.error


if __name__ == '__main__':

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
