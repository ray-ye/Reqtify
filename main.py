from __future__ import annotations
import json
import pygame
import pygame_gui
import sys
from typing import Optional


from settings import Settings
from button import Button, hover_effect
from textbox import TextBox
from form_generator import Form
from data_manager import Playlist, Song, User, Accounts, DataManager


# Initializing objects / variables
accounts = Accounts('account_data.json')
account_list = accounts.get_account()

# for testing:
cur_user = account_list["test1"]
pygame.font.init()

ICON = pygame.image.load("assets/small_logo.png")
pygame.display.set_icon(ICON)

SCREEN = pygame.display.set_mode((Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT))
ui_manager = pygame_gui.UIManager((Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT), "theme.json")


CLOCK = pygame.time.Clock()

big_logo = pygame.transform.scale(pygame.image.load("assets/big_logo.png"), (700 * .5, 300 * .5))
big_logo_rect = big_logo.get_rect(center=(Settings.SCREEN_WIDTH / 2, 250))

data_manager = DataManager()
data_manager.load_data_raw('small.csv')
data_manager.parse_data()

playlist1 = Playlist('playlist1')
playlist1.add_song(data_manager.get_song_by_id('5SuOikwiRyPMVoIQDJUgSV'))
playlist1.add_song(data_manager.get_song_by_id('4qPNDBW1i3p13qLCt0Ki3A'))
playlist1.add_song(data_manager.get_song_by_id('1iJBSr7s7jYXzM8EGcbK5b'))
playlist1.add_song(data_manager.get_song_by_id('6lfxq3CG4xtTiEg7opyCyx'))


# main menu
def login_selection():
    """Handler function for the login screen of the app"""
    pygame.display.set_caption("Reqtify Login")

    # button settings
    button_margin = 140
    button_font = "Arial"
    button_font_size = 35
    font_colour = (30, 30, 30)
    button_colour = (255, 255, 255)
    button_size = (200, 60)  # width, height
    button_radius = 30

    # initialize the prompt buttons
    login_button = Button(
        None,
        pos=(big_logo_rect.center[0], big_logo_rect.center[1] + button_margin),
        text_input="Login",
        font=button_font,
        font_size=button_font_size,
        button_size=button_size,
        font_colour=font_colour,
        button_colour=button_colour,
        radius=button_radius
    )

    register_button = Button(
        None,
        pos=(big_logo_rect.center[0], big_logo_rect.center[1] + button_margin * 1.7),
        text_input="Register",
        font=button_font,
        font_size=button_font_size,
        button_size=button_size,
        font_colour=font_colour,
        button_colour=button_colour,
        radius=button_radius
    )

    buttons = [login_button, register_button]

    while True:

        SCREEN.fill(Settings.BACKGROUND_COLOUR)

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # draw logo onto screen
        SCREEN.blit(big_logo, big_logo_rect)

        # update buttons
        for button in buttons:
            hover_effect(mouse_pos, buttons)
            button.draw(SCREEN)

        # check for user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if login_button.check_hover(mouse_pos):
                    login(register=False)

                if register_button.check_hover(mouse_pos):
                    login(register=True)

        pygame.display.update()


def login(register):
    """Handler function for the login screen"""
    username = ""
    password = ""
    re_password = ""
    error_message = ""

    login_form = Form((Settings.SCREEN_WIDTH / 2, Settings.SCREEN_HEIGHT / 2),
                      ui_manager,
                      "Login",
                      (255, 255, 255),
                      "Arial",
                      20)

    login_form.add_textbox("Username", 230)
    login_form.add_textbox("Password", 230)

    if register:
        login_form.add_textbox("Repeat password", 230)
        login_form.button.change_text("Register")

    for prompter in login_form.get_prompters():
        holder = prompter.get_result()
        if prompter.get_id() in ["#password", "#repeatpassword"]:
            holder.set_text_hidden(True)

    while True:
        SCREEN.fill(Settings.BACKGROUND_COLOUR)
        refresh_rate = CLOCK.tick(60)/1000
        mouse_pos = pygame.mouse.get_pos()
        hover_effect(mouse_pos, [login_form.button])
        login_form.draw(SCREEN)
        ui_manager.update(refresh_rate)
        ui_manager.draw_ui(SCREEN)

        if login_form.error:
            login_form.error_message(error_message, SCREEN)

        for event in pygame.event.get():
            ui_manager.process_events(event)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_object_id == "#username":
                    username = event.text

                if event.ui_object_id == "#password":
                    password = event.text

                if event.ui_object_id == "#repeatpassword":
                    re_password = event.text

            if event.type == pygame.MOUSEBUTTONDOWN:
                if login_form.button.check_hover(mouse_pos):
                    if register:
                        error_message = ""

                        if accounts.error(username, password, re_password):
                            login_form.error = True
                            error_message = accounts.error(username, password, re_password, True)

                        else:
                            accounts.register(username, password)
                            cur_user = account_list[username]
                            main_menu()

                    elif accounts.login(username, password):
                        cur_user = account_list[username]
                        main_menu()

                    else:
                        login_form.error = True
                        error_message = "Username or password incorrect, please try again."

        pygame.display.update()


def main_menu():
    """Handler function for the main menu/home screen of the app"""
    ui_manager2 = pygame_gui.UIManager((Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT), "theme.json")
    pygame.display.set_caption("Reqtify")
    margin = 20
    font = pygame.font.SysFont("Georgia", 75)
    font.set_bold(True)
    textbox = TextBox((150, 500),
                      (font.size("Describe")[0], 50),
                      ui_manager2,
                      "user_input",
                      False)

    textbox.get_result()

    compute_button = Button("assets/compute_button.png",
                            (textbox.get_pos()[0] + textbox.get_dimensions()[0] / 2,
                             textbox.get_pos()[1] + textbox.get_dimensions()[1] + margin * 3),
                            (650 * .4, 150 * .4))

    search_button = Button("assets/search.png",
                           (margin * 3, margin * 3),
                           (50, 50))

    profile_button = Button("assets/profile.png",
                            (Settings.SCREEN_WIDTH - margin * 3, margin * 3),
                            (50, 50))

    buttons = [compute_button, search_button, profile_button]
    title = ["Describe", "Your", "Perfect", "Playlist"]

    while True:
        SCREEN.fill(Settings.BACKGROUND_COLOUR)

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()
        hover_effect(mouse_pos, buttons)

        title_x = textbox.get_pos()[0]
        title_start_height = textbox.get_pos()[1] - font.get_height() * len(title) - margin

        for line in title:
            if line == "Perfect":
                font.set_underline(True)
            text = font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(topleft=(title_x, title_start_height))
            title_start_height += text_rect.height
            SCREEN.blit(text, text_rect)

            font.set_underline(False)

        for button in buttons:
            button.draw(SCREEN)

        textbox.set_pos((title_x, title_start_height))
        refresh_rate = CLOCK.tick(60) / 1000
        ui_manager2.update(refresh_rate)
        ui_manager2.draw_ui(SCREEN)
        pygame.display.update()

        # check for user input
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_object_id == "#user_input":
                    user_input = event.text

            if event.type == pygame.MOUSEBUTTONDOWN:
                if compute_button.check_hover(mouse_pos):
                    pass  # pass user input into a parsing function

                if search_button.check_hover(mouse_pos):
                    pass

            ui_manager2.process_events(event)


def search():
    """Handler function for the search page"""
    pass


def match():
    """Handler function for the match display page"""
    pass


def profile():
    """Handler function for the profile page"""

    pygame.display.set_caption("Reqtify")
    margin = 20

    home_button = Button("assets/home.png",
                           (margin * 3, margin * 3),
                           (50, 50))

    profile_button = Button("assets/profile.png",
                            (Settings.SCREEN_WIDTH - margin * 3, margin * 3),
                            (50, 50))

    cur_user.playlist.load_displays(SCREEN, 130)
    cur_user.playlist.update_display(cur_user)

    buttons = [home_button, profile_button]
    save_buttons = [display.button for display in cur_user.playlist.get_displays().values()]

    while True:
        SCREEN.fill(Settings.BACKGROUND_COLOUR)

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()

        for button in buttons:
            button.draw(SCREEN)

        cur_user.playlist.draw(SCREEN)

        hover_effect(mouse_pos, buttons + save_buttons)
        pygame.display.update()

        # check for user input
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if home_button.check_hover(mouse_pos):
                    pass  # pass user input into a parsing function

                if profile_button.check_hover(mouse_pos):
                    pass

                for display in cur_user.playlist.get_displays().values():
                    if display.button.check_hover(mouse_pos):
                        if display.song.track_id in cur_user.playlist.get_songs():
                            cur_user.playlist.remove_song(display.song)
                            print("Removed: " + display.song.track_name)
                        else:
                            cur_user.playlist.add_song(display.song)
                            print("Added: " + display.song.track_name)

                        cur_user.playlist.update_display(cur_user)

                        print(cur_user.playlist.get_displays())




def choose():
    """handler function for the choose song page"""
    pass


profile()
