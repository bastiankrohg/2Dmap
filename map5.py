# v5 - Debugging additions

import sys
import os
import platform
import argparse
import pygame
from components.menu import menu_screen
from components.map_management import save_map, load_map, reset_map, get_last_used_map, list_maps
from components.drawing import draw_grid, draw_rover, draw_path, draw_hud
from components.game_logic import update_rover_position
from components.constants import *

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping")

def main(map_name, save_enabled):
    print("[DEBUG] Initializing game...")
    try:
        path, rover_pos, resources, obstacles = reset_map()
        rover_angle = 0
        mast_angle = 0
        odometer = 0
        auto_save = save_enabled

        # Check last-used map
        last_used_map = get_last_used_map()
        if last_used_map and os.path.exists(os.path.join(MAPS_DIR, last_used_map)):
            print(f"[DEBUG] Last-used map detected: {last_used_map}")
            path, rover_pos, resources, obstacles = load_map(os.path.join(MAPS_DIR, last_used_map))
        else:
            print("[DEBUG] No valid last-used map found. Starting with a new map.")

        # Display menu
        selected_action, auto_save = menu_screen(screen, auto_save)
        print(f"[DEBUG] Menu returned action: {selected_action}, Auto Save: {auto_save}")
        if selected_action == "load":
            files = list_maps()
            print(f"[DEBUG] Available maps: {files}")
            if files:
                selected_map = files[0]
                path, rover_pos, resources, obstacles = load_map(os.path.join(MAPS_DIR, selected_map))
            else:
                print("[ERROR] No maps found. Starting new map.")
                path, rover_pos, resources, obstacles = reset_map()

        # Game loop
        running = True
        print("[DEBUG] Entering game loop...")
        while running:
            screen.fill(BACKGROUND_COLOR)
            draw_grid(screen)
            draw_path(screen, path)
            draw_rover(screen, rover_pos, rover_angle, mast_angle)
            draw_hud(screen, resources, obstacles, odometer)

            try:
                for event in pygame.event.get():
                    print(f"[DEBUG] Event detected: {event}")
                    if event.type == pygame.QUIT:
                        print("[DEBUG] Quit event detected.")
                        if auto_save:
                            save_map(path, rover_pos, resources, obstacles, name=map_name)
                        running = False

                keys = pygame.key.get_pressed()
                rover_pos, rover_angle, path, odometer, mast_angle = update_rover_position(
                    keys, rover_pos, rover_angle, path, odometer, mast_angle
                )
                print(f"[DEBUG] Rover Pos: {rover_pos}, Angle: {rover_angle}, Mast: {mast_angle}")

                pygame.display.flip()
                pygame.time.Clock().tick(30)

            except Exception as e:
                print(f"[ERROR] Game loop error: {e}")

        print("[DEBUG] Exiting game...")
        pygame.quit()

    except Exception as e:
        print(f"[ERROR] Fatal error in main: {e}")
        pygame.quit()

if __name__ == "__main__":
    try:
        main(map_name="default_map", save_enabled=True)
    except KeyboardInterrupt:
        print("\n[DEBUG] Interrupted by user. Exiting...")
        pygame.quit()
        sys.exit()