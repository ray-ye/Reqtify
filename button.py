"""A module that deals with buttons, and mouse hovering over buttons."""
from typing import Optional
import pygame


def hover_effect(position: tuple[int, int], buttons: list[Button]) -> None:
    """Check if user is hovering over button and change the button accordingly."""

    if any(button.check_hover(position) for button in buttons if button):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


class Button():
    """This class initiates button
    
    Instance Attributes:
    - x_pos: tracks x position of cursor
    - y_pos: tracks y position of cursor
    - image: if button has a saved image
    - text_input: if button have text
    - font: font of the text
    - font_size: font size of the text
    - font_colour: font colour of the text
    - button_colour: colour of the button
    - radius: radius of the circle part of button
    - width: width of button
    - height: height of button
    - text: text in button
    - text_rect: rectangle that makes sure text is in the center of the rectangle.
    - rect: rectangle
    """
    
    x_pos: tuple
    y_pos: tuple
    image: any
    text_input: Optional[str] = None
    font: Optional[str] = None
    font_size: Optional[int] = None
    font_colour: Optional[tuple] = None
    button_colour: Optional[tuple] = None
    radius: Optional[int] = None
    width: float
    height: float
    text: any
    text_rect: any
    rect: any

    def __init__(self, image: any, pos: tuple[int, int], button_size: tuple[int, int],
                 text_input: Optional[str] = None,
                 font: Optional[str] = None,
                 font_size: Optional[int] = None,
                 font_colour: Optional[tuple] = None,
                 button_colour: Optional[tuple] = None,
                 radius: Optional[int] = None
                 ) -> None:

        # -----------initiating attributes-----------
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.image = image
        self.text_input = text_input
        self.font_size = font_size
        if font:
            self.font = pygame.font.SysFont(font, self.font_size, bold=True)
        self.width = button_size[0]
        self.height = button_size[1]
        self.font_colour = font_colour
        self.button_colour = button_colour
        self.radius = radius

        # ----------initiating shapes and surfaces-----------
        if not image:
            # text
            self.text = self.font.render(self.text_input, True, self.font_colour)
            self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

            # rect
            self.rect = pygame.Rect(0, 0, button_size[0], button_size[1])
            self.rect.center = (self.x_pos, self.y_pos)

        else:
            self.image = pygame.image.load(image).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))
            self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def draw(self, screen: any) -> None:
        """Draws the button onto screen"""
        if self.image:
            screen.blit(self.image, self.rect)

        else:
            pygame.draw.rect(screen, self.button_colour, self.rect, border_radius=self.radius)
            screen.blit(self.text, self.text_rect)

    def check_hover(self, position: tuple) -> bool:
        """Checks if button has been clicked based on the current position of the mouse."""

        if (
                position[0] in range(self.rect.left, self.rect.right)
                and position[1] in range(self.rect.top, self.rect.bottom)
        ):

            return True
        return False

    def set_pos(self, x: float, y: float) -> None:
        """Sets the x, y positions and renders text"""
        self.x_pos = x
        self.y_pos = y

        self.text = self.font.render(self.text_input, True, self.font_colour)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.x_pos, self.y_pos)

    def get_pos(self) -> tuple:
        """Returns x_pos and y_pos"""
        return self.x_pos, self.y_pos

    def get_dimensions(self) -> tuple:
        """Returns width and height"""
        return self.width, self.height

    def change_text(self, new_text: any) -> None:
        """Changes the text"""
        self.text = self.font.render(new_text, True, self.font_colour)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update_image(self) -> None:
        """Updates the image"""
        self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))


if __name__ == "__main__":
    # pass
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
