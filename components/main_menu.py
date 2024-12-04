import pygame
import sys
from components.constants import WIDTH, HEIGHT

import os

def get_saved_maps():
    return [f.split(".json")[0] for f in os.listdir("maps/") if f.endswith(".json")]

# Initialize pygame
pygame.init()

# Screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping - Main Menu")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont(None, 48)
menu_font = pygame.font.SysFont(None, 36)
dropdown_font = pygame.font.SysFont(None, 28)

# Colors
BACKGROUND_COLOR = (30, 30, 30)
BUTTON_COLOR = (50, 50, 50)
BUTTON_HOVER_COLOR = (70, 70, 70)
TEXT_COLOR = (255, 255, 255)
DROPDOWN_COLOR = (40, 40, 40)
DROPDOWN_HOVER_COLOR = (60, 60, 60)

# Menu structure
def render_button(text, x, y, width, height, hover=False):
    color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, (x, y, width, height))
    text_surface = menu_font.render(text, True, TEXT_COLOR)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))

def render_dropdown(options, selected_index, x, y, width, height, expanded):
    # Draw selected option
    selected_color = DROPDOWN_HOVER_COLOR if expanded else DROPDOWN_COLOR
    pygame.draw.rect(screen, selected_color, (x, y, width, height))
    selected_text = dropdown_font.render(options[selected_index], True, TEXT_COLOR)
    screen.blit(selected_text, (x + 5, y + (height - selected_text.get_height()) // 2))

    if expanded:
        # Draw dropdown options
        for i, option in enumerate(options):
            option_y = y + height * (i + 1)
            option_color = DROPDOWN_HOVER_COLOR if i == selected_index else DROPDOWN_COLOR
            pygame.draw.rect(screen, option_color, (x, option_y, width, height))
            option_text = dropdown_font.render(option, True, TEXT_COLOR)
            screen.blit(option_text, (x + 5, option_y + (height - option_text.get_height()) // 2))

def main_menu():
    running = True
    dropdown_expanded = False
    dropdown_options = get_saved_maps()
    selected_index = 0

    while running:
        screen.fill(BACKGROUND_COLOR)

        # Draw menu title
        title_surface = title_font.render("Rover Mapping", True, TEXT_COLOR)
        screen.blit(title_surface, ((WIDTH - title_surface.get_width()) // 2, 50))

        # Button areas
        new_map_button = pygame.Rect(WIDTH // 2 - 100, 200, 200, 50)
        load_map_button = pygame.Rect(WIDTH // 2 - 100, 300, 200, 50)
        dropdown_area = pygame.Rect(WIDTH // 2 - 100, 360, 200, 40)

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check for hover
        hover_new_map = new_map_button.collidepoint(mouse_x, mouse_y)
        hover_load_map = load_map_button.collidepoint(mouse_x, mouse_y)

        # Draw buttons
        render_button("Start New Map", new_map_button.x, new_map_button.y, new_map_button.width, new_map_button.height, hover_new_map)
        render_button("Load Map", load_map_button.x, load_map_button.y, load_map_button.width, load_map_button.height, hover_load_map)

        # Draw dropdown menu
        render_dropdown(dropdown_options, selected_index, dropdown_area.x, dropdown_area.y, dropdown_area.width, dropdown_area.height, dropdown_expanded)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hover_new_map:
                    return "new", None  # Start a new map
                if hover_load_map and not dropdown_expanded:
                    dropdown_expanded = True
                elif dropdown_expanded and dropdown_area.collidepoint(mouse_x, mouse_y):
                    dropdown_expanded = False  # Close dropdown
                elif dropdown_expanded:
                    # Check if a dropdown option is clicked
                    for i in range(len(dropdown_options)):
                        option_y = dropdown_area.y + dropdown_area.height * (i + 1)
                        option_rect = pygame.Rect(dropdown_area.x, option_y, dropdown_area.width, dropdown_area.height)
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            selected_index = i
                            dropdown_expanded = False
                            return "load", dropdown_options[selected_index]  # Load the selected map

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    map_choice, map_name = main_menu()
    print(f"Selected option: {map_choice}, Map: {map_name}")