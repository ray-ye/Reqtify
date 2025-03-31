"""This is a module that contains a Form class that is responsible for building and executing form opertaions"""

from typing import Any
import pygame
from textbox import TextBox
from button import Button


class Form():
    """
    A dynamic, self-adjusting form container for user input in Pygame applications.

    Instance Attributes:
    - x_pos (int): Horizontal center position of the form
    - y_pos (int): Vertical center position of the form
    - ui_manager (pygame_gui.UIManager): GUI manager for pygame_gui elements
    - rect (pygame.Rect): The bounding rectangle of the form background
    - prompter (dict[str, TextBox]): Dictionary mapping labels to TextBox objects
    - margin (int): Vertical spacing between form elements (default: 120px)
    - padding (int): Inner padding around form edges (default: 70px)
    - button (Button): The form's submission button
    - background_colour (tuple[int, int, int]): RGB color for form background
    - font_size (int): Font size for field labels
    - font (pygame.font.Font): Font object for rendering labels
    - error (bool): Flag indicating if the form contains validation errors

    >>> import pygame
    >>> import pygame_gui
    >>> _ = pygame.init()
    >>> screen = pygame.display.set_mode((800, 600))
    >>> ui_manager = pygame_gui.UIManager((800, 600))
    >>> form = Form((400, 300), ui_manager, "Submit", (255, 255, 255), "Arial", 20)
    >>> form.add_textbox("Username", 200)
    >>> form.add_textbox("Password", 200)
    >>> form.draw(screen)
    """
    x_pos: tuple
    y_pos: tuple
    ui_manager: Any
    rect: Any
    prompter: dict
    margin: int
    padding: int
    button: Button
    background_colour: tuple
    font_size: Any
    font: Any
    error: bool

    def __init__(self, position: tuple, manager: Any, button_text: str,
                 background_colour: tuple, font: Any, font_size: int) -> None:
        """Initialize a new form container.

        Preconditions:
            - position is a tuple of (x, y) integers within screen bounds
            - manager is an initialized pygame_gui.UIManager
            - button_text is a non-empty string
            - background_colour is a valid RGB tuple
            - font is a string naming an available system font
            - font_size is a positive integer
        """
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

    def add_textbox(self, title: Any, width: float) -> None:
        """Add a new labeled input field to the form.

        Preconditions:
            - title is a non-empty string
            - width > 0
            - The form has enough vertical space to add another field
        """
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

        self.prompter[title] = TextBox(position, (width, 45), self.ui_manager,
                                       "#" + title.lower().replace(" ", ""), True)
                                       
    def draw(self, screen: Any) -> None:
        """Render all form elements to the specified surface.

        Preconditions:
            - screen is a valid pygame.Surface
            - pygame display is initialized
            - All form elements are properly initialized
        """
        pygame.draw.rect(screen, self.background_colour, self.rect, border_radius=30)
        self.button.draw(screen)

        for prompter in self.prompter:
            textbox = self.prompter[prompter]
            text = self.font.render(prompter, True, (30, 30, 30))
            screen.blit(text, (textbox.rect.topleft[0], textbox.rect.topleft[1] - 25))

    def get_prompters(self) -> Any:
        """Retrieve all text input fields in the form."""
        return self.prompter.values()

    def error_message(self, message: str, screen: Any) -> None:
        """Display a validation error message below the last form field."""

        font = pygame.font.SysFont("Arial", 9)
        text = font.render(message, True, (144, 8, 8))
        text_rect = text.get_rect(center=(self.rect.centerx, list(self.get_prompters())[-1].rect.bottomleft[1] + 20))
        screen.blit(text, text_rect)

    def check_error(self) -> Any:
        """Check the form's error state."""
        return self.error


if __name__ == '__main__':

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    import doctest
    doctest.testmod()
