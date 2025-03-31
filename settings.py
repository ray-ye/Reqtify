"""This module contains a data class for the app"""
from typing import Any
import pygame


class Settings:
    """A settings data class storing all settings attributes for the app

    Instance Attributes:
    - display_info: information on display
    - SCREEN_WIDTH: width of screen
    - SCREEN_HEIGHT: Height of screen
    - BACKGROUND_COLOUR: background colour
    """
    display_info: Any
    SCREEN_HEIGHT: float
    SCREEN_WIDTH: float
    BACKGROUND_COLOUR: tuple
    pygame.init()
    display_info = pygame.display.Info()

    SCREEN_WIDTH = display_info.current_w / 1.5
    SCREEN_HEIGHT = display_info.current_h - 130
    BACKGROUND_COLOUR = (33, 33, 33)


if __name__ == '__main__':

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    import doctest
    doctest.testmod()
