"""This is a module taht contains a Form class that is responsible for building and executing form opertaions"""
from textbox import TextBox
from button import Button
import pygame


class Form:
    """A class for creating a fully functional form

    Instance Attributes:
    - position: a tuple of x and y coordinate
    - manager: manager for python_ui (textbox)
    - button_text: text of the form submit button
    - backgound_colour: background colour of the form
    - font: font of text on the form
    - font_size: size font of text on the form
    - rect: the rect object of the form
    - prompter: a dictionary collection of textbox objects (textbox mapped to song_id)
    - button: the button object of this form
    - error: whether there's an error in the inputs
    """

    def __init__(self, position, manager, button_text, background_colour, font, font_size):
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
                             (217, 217, 217),
                             35)
        self.background_colour = background_colour
        self.font_size = font_size
        self.font = pygame.font.SysFont(font, font_size)
        self.error = False

    def add_textbox(self, title, width) -> None:
        """add a textbox to the form"""

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

    def draw(self, screen) -> None:
        """draw entire form onto screen"""

        pygame.draw.rect(screen, self.background_colour, self.rect, border_radius=30)
        self.button.draw(screen)

        for prompter in self.prompter:
            textbox = self.prompter[prompter]
            text = self.font.render(prompter, True, (30, 30, 30))
            screen.blit(text, (textbox.rect.topleft[0], textbox.rect.topleft[1] - 25))

    def get_prompters(self):
        """Get all textboxes of the form"""

        return self.prompter.values()

    def error_message(self, message, screen):
        """Draw error message onto screen"""

        font = pygame.font.SysFont("Arial", 9)
        text = font.render(message, True, (144, 8, 8))
        text_rect = text.get_rect(center=(self.rect.centerx, list(self.get_prompters())[-1].rect.bottomleft[1] + 20))
        screen.blit(text, text_rect)

    def check_error(self):
        """See if there are errors to the inputs of the form"""

        return self.error
