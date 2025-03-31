from __future__ import annotations
import json
import random
import pygame
import pygame_gui
import sys
from typing import Optional


from settings import Settings
from button import Button, hover_effect
from textbox import TextBox
from form_generator import Form
from data_manager import Playlist, Song, User, Accounts, SongManager
from feature_guesser import MusicFeatureGuesser
from decision_tree import DecisionTree

# Initializing objects / variables
accounts = Accounts('account_data.json')
account_list = accounts.get_account()
cur_user = account_list["init"]
pygame.font.init()

ICON = pygame.image.load("assets/small_logo.png")
pygame.display.set_icon(ICON)

screen = pygame.display.set_mode((Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT))
ui_manager = pygame_gui.UIManager((screen.get_width(), screen.get_height()), "theme.json")


CLOCK = pygame.time.Clock()

big_logo = pygame.image.load("assets/big_logo.png").convert_alpha()
big_logo = pygame.transform.smoothscale(big_logo, (pygame.image.load("assets/compute_button.png").get_width(),
                                                   pygame.image.load("assets/compute_button.png").get_height()))

big_logo_rect = big_logo.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 140))

#  User input parsing
guesser = MusicFeatureGuesser("reference_data.csv")
tolerance = 5

# song manager
song_manager = SongManager()
song_manager.load_data_raw("dataset.csv")
song_manager.parse_data()

# decision Tree
decision_tree = DecisionTree(None, [])
decision_tree.build_tree("songs.csv")


# main menu
def login_selection():
    """Handler function for the login screen of the app"""
    global screen

    pygame.display.set_caption("Reqtify Login")

    # button settings
    button_margin = 140
    button_font = "Arial"
    button_font_size = 30
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

        screen.fill(Settings.BACKGROUND_COLOUR)

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # draw logo onto screen
        screen.blit(big_logo, big_logo_rect)

        # update buttons
        for button in buttons:
            hover_effect(mouse_pos, buttons)
            button.draw(screen)

        # check for user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

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

    login_form = Form((screen.get_width() / 2, screen.get_height() / 2),
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
        screen.fill(Settings.BACKGROUND_COLOUR)
        refresh_rate = CLOCK.tick(60)/1000
        mouse_pos = pygame.mouse.get_pos()
        hover_effect(mouse_pos, [login_form.button])
        login_form.draw(screen)
        ui_manager.update(refresh_rate)
        ui_manager.draw_ui(screen)

        if login_form.error:
            login_form.error_message(error_message, screen)

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
    ui_manager2 = pygame_gui.UIManager((screen.get_width(), screen.get_height()), "theme.json")
    pygame.display.set_caption("Reqtify")
    margin = 20
    error_message = ""
    user_input = ""
    font = pygame.font.SysFont("Georgia", 75)
    font.set_bold(True)
    textbox = TextBox((screen.get_width() / 2 - font.size("Describe")[0] / 2, 500),
                      (font.size("Describe")[0], 50),
                      ui_manager2,
                      "user_input",
                      False)

    textbox.get_result()

    compute_button = Button("assets/compute_button.png",
                            (textbox.get_pos()[0] + textbox.get_dimensions()[0] / 2,
                             textbox.get_pos()[1] + textbox.get_dimensions()[1] + margin * 3),
                            (pygame.image.load("assets/compute_button.png").get_width() * .7,
                             pygame.image.load("assets/compute_button.png").get_height() * .7))

    search_button = Button("assets/search.png",
                           (margin * 3, margin * 3),
                           (50, 50))

    profile_button = Button("assets/profile.png",
                            (screen.get_width() - margin * 3, margin * 3),
                            (50, 50))

    buttons = [compute_button, search_button, profile_button]
    title = ["Describe", "Your", "Perfect", "Music Playlist"]

    font2 = pygame.font.SysFont("Arial", 20)
    font3 = pygame.font.SysFont("Arial", 15)

    text2 = font2.render("Loading...", True, (200, 200, 200))
    text_rect2 = text2.get_rect(
        center=(screen.get_width() / 2, compute_button.get_pos()[1] + compute_button.get_dimensions()[1] + 40))



    while True:
        screen.fill(Settings.BACKGROUND_COLOUR)
        text3 = font3.render(error_message, True, (200, 200, 200))
        text_rect3 = text3.get_rect(
            center=(screen.get_width() / 2, compute_button.get_pos()[1] + compute_button.get_dimensions()[1] + 40))
        # get mouse position
        mouse_pos = pygame.mouse.get_pos()
        hover_effect(mouse_pos, buttons)

        title_x = textbox.get_pos()[0]
        title_start_height = textbox.get_pos()[1] - font.get_height() * len(title) - margin

        for line in title:
            if line == "Perfect":
                font.set_underline(True)
            if line == "Music Playlist":
                font = pygame.font.SysFont("Georgia", 55)
                font.set_bold(True)
                title_start_height += 15
            text = font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(topleft=(title_x, title_start_height))
            title_start_height += text_rect.height
            screen.blit(text, text_rect)
            screen.blit(text3, text_rect3)
            font = pygame.font.SysFont("Georgia", 75)

            font.set_underline(False)

        for button in buttons:
            button.draw(screen)

        textbox.set_pos((title_x, title_start_height))
        refresh_rate = CLOCK.tick(60) / 1000
        ui_manager2.update(refresh_rate)
        ui_manager2.draw_ui(screen)
        pygame.display.update()

        # check for user input
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                accounts.save()
                pygame.quit()
                sys.exit()

            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_object_id == "user_input":
                    user_input = event.text
                    error_message = ""

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if compute_button.check_hover(mouse_pos):
                        if len(user_input.split(" ")) < 5:
                            error_message = "We need a little more info, please describe more!"

                        else:
                            screen.blit(text2, text_rect2)
                            pygame.display.update()
                            delay = random.randint(2500, 3000)
                            pygame.time.delay(delay)
                            output(user_input)  # pass user input into a parsing function

                    if profile_button.check_hover(mouse_pos):
                        profile()

                    if search_button.check_hover(mouse_pos):
                        search()

            ui_manager2.process_events(event)


def output(user_input):
    """handler function for the choose song page"""
    global screen
    playlist = Playlist("Search result")
    pygame.display.set_caption("Reqtify")
    features = guesser.predict_features(user_input, tolerance)
    result = set(decision_tree.children([bool(x) for x in features]))
    result = [song_manager.get_song_by_id(track_id) for track_id in result if
              song_manager.get_song_by_id(track_id).track_name.isascii()]

    num_output = random.randint(30, 69)

    for i in range(num_output):
        song_ind = random.randint(0, len(result) - 1)
        playlist.add_song(result[song_ind])

    margin = 20

    font = pygame.font.SysFont("Arial", 30)
    font2 = pygame.font.SysFont("Arial", 16)
    text = font.render(f"{len(playlist)} songs found", True, (200, 200, 200))
    text2 = font.render("", True, (200, 200, 200))

    text_rect = text.get_rect(center=(screen.get_width() / 2 + 20, 60))
    text2_rect = text2.get_rect(center=(screen.get_width() / 2, 110))
    text_border = pygame.image.load("assets/title_border2.png")
    text_border = pygame.transform.smoothscale(text_border, (text_rect.width + 100,
                                                             text_border.get_height() * ((text_rect.width + 100) / text_border.width)))
    text_border_rect = text_border.get_rect()
    text_border_rect.center = (text_rect.centerx - 20, text_rect.centery - 3)

    home_button = Button("assets/home.png",
                         (margin * 3, margin * 3),
                         (50, 50))

    profile_button = Button("assets/profile.png",
                            (screen.get_width() - margin * 3, margin * 3),
                            (50, 50))

    up_button = Button("assets/up_button.png",
                       (screen.get_width() / 2 - margin * 1.5, screen.get_height() - 65),
                       (50, 50))

    down_button = Button("assets/down_button.png",
                         (screen.get_width() / 2 + margin * 1.5, screen.get_height() - 65),
                         (50, 50))

    playlist.load_displays(screen, 150, list(playlist.get_songs().values()))
    playlist.update_display(cur_user)
    display_start_row = 0

    song_holder = list(playlist.get_songs().values())
    buttons = [home_button, profile_button, up_button, down_button]

    while True:
        screen.fill(Settings.BACKGROUND_COLOUR)
        save_buttons = [display.button for display in playlist.get_displays().values()]

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()

        for button in buttons:
            button.draw(screen)

        playlist.draw(screen)
        hover_effect(mouse_pos, buttons + save_buttons)
        screen.blit(text_border, text_border_rect)
        screen.blit(text, text_rect)
        screen.blit(text2, text2_rect)
        pygame.display.update()

        # check for user input
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                accounts.save()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if home_button.check_hover(mouse_pos):
                        main_menu()  # pass user input into a parsing function

                    if profile_button.check_hover(mouse_pos):
                        profile()

                    if up_button.check_hover(mouse_pos):
                        if list(playlist.get_displays().values())[0].song != song_holder[0]:
                            display_start_row -= 2
                            playlist.load_displays(screen, 150, song_holder[display_start_row:])
                            playlist.update_display(cur_user)

                    if down_button.check_hover(mouse_pos):
                        if len(song_holder[display_start_row:]) > 2:
                            display_start_row += 2
                            playlist.load_displays(screen, 150, song_holder[display_start_row:])
                            playlist.update_display(cur_user)

                    for display in playlist.get_displays().values():

                        if display.button.check_hover(mouse_pos):
                            if display.song.track_id in cur_user.playlist.get_songs():
                                cur_user.playlist.remove_song(display.song)
                                text2 = font2.render(f"\"{display.song.track_name}\" removed to profile", True,
                                                     (200, 200, 200))
                                text2_rect = text2.get_rect(center=(screen.get_width() / 2, 110))
                                print("Removed: " + display.song.track_name)
                            else:
                                cur_user.playlist.add_song(display.song)
                                text2 = font2.render(f"\"{display.song.track_name}\" added from profile", True,
                                                     (200, 200, 200))
                                text2_rect = text2.get_rect(center=(screen.get_width() / 2, 110))
                                print("Added: " + display.song.track_name)

                            playlist.update_display(cur_user)

            if event.type == pygame.MOUSEWHEEL:
                if event.y < 0:
                    if list(playlist.get_displays().values())[0].song != song_holder[0]:
                        display_start_row -= 2
                        playlist.load_displays(screen, 150, song_holder[display_start_row:])
                        playlist.update_display(cur_user)

                if down_button.check_hover(mouse_pos) or event.y > 0:
                    if len(song_holder[display_start_row:]) > 2:
                        display_start_row += 2
                        playlist.load_displays(screen, 150, song_holder[display_start_row:])
                        playlist.update_display(cur_user)


def search():
    """Handler function for the search page"""
    ui_manager3 = pygame_gui.UIManager((screen.get_width(), screen.get_height()), "theme.json")
    pygame.display.set_caption("Reqtify")
    margin = 20
    user_input2 = ""
    error_message = ""
    font = pygame.font.SysFont("Georgia", 40)
    font.set_bold(True)
    font2 = pygame.font.SysFont("Georgia", 15)

    textbox = TextBox((screen.get_width() / 2 - font.size("compare music")[0] / 2, 360),
                      (font.size("compare music")[0], 50),
                      ui_manager3,
                      "user_input",
                      False)

    textbox.get_result()

    search_button = Button("assets/search_button.png",
                            (textbox.get_pos()[0] + textbox.get_dimensions()[0] / 2,
                             textbox.get_pos()[1] + textbox.get_dimensions()[1] + margin * 3),
                            (pygame.image.load("assets/search_button.png").get_width() * .7,
                             pygame.image.load("assets/search_button.png").get_height() * .7))

    home_button = Button("assets/home.png",
                           (margin * 3, margin * 3),
                           (50, 50))

    profile_button = Button("assets/profile.png",
                            (screen.get_width() - margin * 3, margin * 3),
                            (50, 50))

    buttons = [home_button, search_button, profile_button]
    title = ["Search up your friend", "to compare music taste!"]

    while True:
        screen.fill(Settings.BACKGROUND_COLOUR)

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()
        hover_effect(mouse_pos, buttons)

        title_x = textbox.get_pos()[0]
        title_start_height = textbox.get_pos()[1] - font.get_height() * len(title) - margin + 20

        text2 = font2.render(error_message, True, (200, 200, 200))
        text_rect2 = text2.get_rect(
            center=(screen.width / 2, search_button.get_pos()[1] + search_button.get_dimensions()[1] + margin * 2))

        for line in title:
            text = font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.width/2, title_start_height))
            title_start_height += text_rect.height
            screen.blit(text, text_rect)

            font.set_underline(False)

        screen.blit(text2, text_rect2)

        for button in buttons:
            button.draw(screen)

        textbox.set_pos((title_x, title_start_height))
        refresh_rate = CLOCK.tick(60) / 1000
        ui_manager3.update(refresh_rate)
        ui_manager3.draw_ui(screen)
        pygame.display.update()

        # check for user input
        for event in pygame.event.get():
            ui_manager3.process_events(event)

            if event.type == pygame.QUIT:
                accounts.save()
                pygame.quit()
                sys.exit()

            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:

                if event.ui_object_id == "user_input":

                    user_input2 = event.text

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if search_button.check_hover(mouse_pos):
                        if user_input2 in account_list:
                            match(account_list[user_input2])  # pass user input into a parsing function

                        else:
                            error_message = "User not found, please try again."

                    if profile_button.check_hover(mouse_pos):
                        profile()

                    if home_button.check_hover(mouse_pos):
                        main_menu()


def match(other_user):
    """Handler function for the match display page"""
    pygame.display.set_caption("Reqtify")
    margin = 75
    button_margin = 20
    match_percent = cur_user.playlist.taste_match(other_user.playlist)
    fun_message = ""

    font1 = pygame.font.SysFont("Georgia", 75)
    font1.set_bold(True)
    font2 = pygame.font.SysFont("Georgia", 45)
    font2.set_bold(True)
    font3 = pygame.font.SysFont("Georgia", 20)

    if match_percent < 25:
        fun_message = ["You'd survive a car ride together... as long", "as you take turns with the aux"]

    if match_percent < 50:
        fun_message = ["You might not vibe at the same frequency yet...", "but hey, opposites attract, right?"]

    if match_percent < 75:
        fun_message = ["One of you starts the song, the other finishes", "the lyrics. It's getting real."]

    if match_percent <= 100:
        fun_message = ["Did you grow up in the same headphones or what?", "Your playlists are practically twins."]

    home_button = Button("assets/home.png",
                           (button_margin * 3, button_margin * 3),
                           (50, 50))

    profile_button = Button("assets/profile.png",
                            (screen.get_width() - button_margin * 3, button_margin * 3),
                            (50, 50))

    buttons = [home_button, profile_button]

    while True:
        screen.fill(Settings.BACKGROUND_COLOUR)

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()
        hover_effect(mouse_pos, buttons)

        text1 = font1.render(f"{match_percent}%", True, (200, 200, 200))

        text2 = font2.render(f"{cur_user.name} + {other_user.name}", True, (200, 200, 200))

        text1_rect = text1.get_rect(center=(screen.width/2, screen.height/2))
        text2_rect = text2.get_rect(center=(text1_rect.centerx, text1_rect.y - text1_rect.height))

        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)
        text3_start_height = text1_rect.y + text1_rect.height + margin
        for line in fun_message:
            text = font3.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(text1_rect.centerx, text3_start_height))
            text3_start_height += text_rect.height
            screen.blit(text, text_rect)

        for button in buttons:
            button.draw(screen)

        pygame.display.update()

        # check for user input
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                accounts.save()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    if profile_button.check_hover(mouse_pos):
                        profile()

                    if home_button.check_hover(mouse_pos):
                        main_menu()


def profile():
    """Handler function for the profile page"""
    global screen
    pygame.display.set_caption("Reqtify")
    margin = 20

    font = pygame.font.SysFont("Arial", 25)
    font2 = pygame.font.SysFont("Arial", 16)
    text1 = font.render(f"Your profile ({len(cur_user.playlist.get_songs())} songs)", True, (200, 200, 200))
    text2 = font.render("", True, (200, 200, 200))

    text1_rect = text1.get_rect(center=(screen.get_width() / 2, 60))
    text2_rect = text2.get_rect(center=(screen.get_width() / 2, 125))
    text1_border = pygame.image.load("assets/title_border1.png")
    text1_border = pygame.transform.smoothscale(text1_border, (text1_rect.width + 100,
                                                text1_border.get_height() * ((text1_rect.width + 100) / text1_border.width)))
    text1_border_rect = text1_border.get_rect()
    text1_border_rect.center = (text1_rect.centerx, text1_rect.centery - 3)

    home_button = Button("assets/home.png",
                           (margin * 3, margin * 3),
                           (50, 50))

    profile_button = Button("assets/profile.png",
                            (screen.get_width() - margin * 3, margin * 3),
                            (50, 50))

    up_button = Button("assets/up_button.png",
                            (screen.get_width() / 2 - screen.get_width() / 4 - margin * 1.5, screen.get_height() - 65),
                            (50, 50))

    down_button = Button("assets/down_button.png",
                            (screen.get_width() / 2 - screen.get_width() / 4 + margin * 1.5, screen.get_height() - 65),
                            (50, 50))

    cur_user.playlist.load_displays(screen, 150, list(cur_user.playlist.get_songs().values()), True)
    cur_user.playlist.update_display(cur_user)
    display_start_row = 0

    song_holder = list(cur_user.playlist.get_songs().values())
    buttons = [home_button, profile_button, up_button, down_button]

    stats = cur_user.playlist.playlist_profile()

    while True:
        screen.fill(Settings.BACKGROUND_COLOUR)

        stat_starting_height = 175
        save_buttons = [display.button for display in cur_user.playlist.get_displays().values()]

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()

        for button in buttons:
            button.draw(screen)

        for stat in stats:
            if isinstance(stats[stat], float):
                text = font.render(f"{stat}: {stats[stat]}%", True, (30, 30, 30))
            else:
                text = font.render(f"{stat}: {stats[stat]}", True, (30, 30, 30))

            text_rect = text.get_rect(topleft=(screen.width/2 + margin * 4, stat_starting_height))
            stat_starting_height += 80

            text_border = pygame.image.load("assets/title_border3.png")
            text_border = pygame.transform.smoothscale(text_border, (text_rect.width + margin * 6, 75))
            text_border_rect = text_border.get_rect()
            text_border_rect.center = (text_rect.x + text_rect.width / 2 + 45, text_rect.y + text_rect.height / 2)

            screen.blit(text_border, text_border_rect)
            screen.blit(text, text_rect)

        cur_user.playlist.draw(screen)

        hover_effect(mouse_pos, buttons + save_buttons)
        screen.blit(text1_border, text1_border_rect)
        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)
        pygame.display.update()

        # check for user input
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                accounts.save()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if home_button.check_hover(mouse_pos):
                        main_menu()  # pass user input into a parsing function

                    if profile_button.check_hover(mouse_pos):
                        pass

                    if up_button.check_hover(mouse_pos):
                        displays = cur_user.playlist.get_displays()
                        if len(displays) > 0 and list(displays.values())[0].song != song_holder[0]:
                            display_start_row -= 1
                            cur_user.playlist.load_displays(screen, 150, song_holder[display_start_row:], True)
                            cur_user.playlist.update_display(cur_user)

                    if down_button.check_hover(mouse_pos):
                        if len(song_holder[display_start_row:]) > 1:
                            display_start_row += 1
                            cur_user.playlist.load_displays(screen, 150, song_holder[display_start_row:], True)
                            cur_user.playlist.update_display(cur_user)

                    for display in cur_user.playlist.get_displays().values():

                        if display.button.check_hover(mouse_pos):
                            if display.song.track_id in cur_user.playlist.get_songs():
                                cur_user.playlist.remove_song(display.song)
                                text2 = font2.render(f"\"{display.song.track_name}\" removed to profile", True,
                                                     (200, 200, 200))
                                text2_rect = text2.get_rect(center=(screen.get_width() / 2, 125))

                            else:
                                cur_user.playlist.add_song(display.song)
                                text2 = font2.render(f"\"{display.song.track_name}\" added from profile", True,
                                                     (200, 200, 200))
                                text2_rect = text2.get_rect(center=(screen.get_width() / 2, 125))

                            cur_user.playlist.update_display(cur_user)

            if event.type == pygame.MOUSEWHEEL:
                if event.y < 0:
                    if list(cur_user.playlist.get_displays().values())[0].song != song_holder[0]:
                        display_start_row -= 1
                        cur_user.playlist.load_displays(screen, 150, song_holder[display_start_row:], True)
                        cur_user.playlist.update_display(cur_user)

                if down_button.check_hover(mouse_pos) or event.y > 0:
                    if len(song_holder[display_start_row:]) > 1:
                        display_start_row += 1
                        cur_user.playlist.load_displays(screen, 150, song_holder[display_start_row:], True)
                        cur_user.playlist.update_display(cur_user)


login_selection()
