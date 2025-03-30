"""This module contains a data class for the app"""
import pygame


class Settings:
    """A settings data class storing all settings attributes for the app"""
    pygame.init()
    display_info = pygame.display.Info()

    SCREEN_WIDTH = display_info.current_w / 1.5 # 650
    SCREEN_HEIGHT = display_info.current_h - 130
    BACKGROUND_COLOUR = (33, 33, 33)
