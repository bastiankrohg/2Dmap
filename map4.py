# v4 - Add save/load map, and last known rover position

import pygame
import math
import sys
import json
from datetime import datetime
import os

import argparse

# Command-line argument parsing
parser = argparse.ArgumentParser(description="Rover Mapping Tool")
parser.add_argument("--no-auto-save", action="store_true", help="Disable automatic saving on exit")
args = parser.parse_args()

# Auto-save toggle
auto_save = not args.no_auto_save

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 20
ROVER_COLOR = (0, 255, 0)
MAST_COLOR = (0, 0, 255)
RESOURCE_COLOR = (0, 255, 255)
OBSTACLE_COLOR = (255, 0, 0)
PATH_COLOR = (200, 200, 200)
BACKGROUND_COLOR = (0, 0, 0)
RESOURCE_DISTANCE = 15
OBSTACLE_DISTANCE = 15
OBSTACLE_LENGTH = 30
HUD_FONT_SIZE = 24
MAPS_DIR = "maps"

# Ensure maps directory exists
os.makedirs(MAPS_DIR, exist_ok=True)

# Screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping")
clock = pygame.time.Clock()

# Fonts
hud_font = pygame.font.SysFont(None, HUD_FONT_SIZE)
list_font = pygame.font.SysFont(None, 18)

# Map data
rover_pos = [WIDTH // 2, HEIGHT // 2]
rover_angle = 0
mast_angle = 0
mast_offset = 0
rover_speed = 5
path = []
resources = []
obstacles = []
odometer = 0

# Flags
show_resource_list = False
show_obstacle_list = False
place_resource_pressed = False
place_obstacle_pressed = False

# Utility functions
def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))

def draw_rover():
    pygame.draw.circle(screen, ROVER_COLOR, (int(rover_pos[0]), int(rover_pos[1])), GRID_SIZE // 2)

def draw_path():
    for pos in path:
        pygame.draw.circle(screen, PATH_COLOR, (int(pos[0]), int(pos[1])), 2)

def draw_arrows():
    rover_end_x = rover_pos[0] + math.cos(math.radians(rover_angle)) * 40
    rover_end_y = rover_pos[1] - math.sin(math.radians(rover_angle)) * 40
    pygame.draw.line(screen, ROVER_COLOR, rover_pos, (rover_end_x, rover_end_y), 3)

    mast_end_x = rover_pos[0] + math.cos(math.radians(mast_angle)) * 40
    mast_end_y = rover_pos[1] - math.sin(math.radians(mast_angle)) * 40
    pygame.draw.line(screen, MAST_COLOR, rover_pos, (mast_end_x, mast_end_y), 3)

def draw_resources():
    for resource in resources:
        pygame.draw.circle(screen, RESOURCE_COLOR, (int(resource[0]), int(resource[1])), GRID_SIZE // 4)

def draw_obstacles():
    for obstacle in obstacles:
        pygame.draw.line(screen, OBSTACLE_COLOR, obstacle[0], obstacle[1], 3)

def draw_hud():
    hud_surface = hud_font.render(
        f"Resources: {len(resources)} | Obstacles: {len(obstacles)} | Odometer: {odometer:.2f} cm",
        True,
        (255, 255, 255),
    )
    screen.blit(hud_surface, (10, 10))

def draw_lists():
    if show_resource_list:
        draw_overlay("Resource List", resources)
    if show_obstacle_list:
        draw_overlay("Obstacle List", obstacles)

def draw_overlay(title, items):
    overlay_width = WIDTH // 3
    overlay_height = HEIGHT // 2
    overlay_x = (WIDTH - overlay_width) // 2
    overlay_y = HEIGHT - overlay_height - 10

    pygame.draw.rect(screen, (50, 50, 50, 180), (overlay_x, overlay_y, overlay_width, overlay_height))
    pygame.draw.rect(screen, (255, 255, 255), (overlay_x, overlay_y, overlay_width, overlay_height), 2)

    header_text = list_font.render(title, True, (255, 255, 255))
    screen.blit(header_text, (overlay_x + 10, overlay_y + 10))

    for i, item in enumerate(items):
        if isinstance(item[0], tuple):
            start, end = item
            display_text = f"{i + 1}: ({round(start[0], 2)}, {round(start[1], 2)}) to ({round(end[0], 2)}, {round(end[1], 2)})"
        else:
            display_text = f"{i + 1}: ({round(item[0], 2)}, {round(item[1], 2)})"
        item_surface = list_font.render(display_text, True, (255, 255, 255))
        screen.blit(item_surface, (overlay_x + 10, overlay_y + 30 + i * 20))

def compute_resource_position():
    x = rover_pos[0] + RESOURCE_DISTANCE * math.cos(math.radians(mast_angle))
    y = rover_pos[1] - RESOURCE_DISTANCE * math.sin(math.radians(mast_angle))
    return [x, y]

def compute_obstacle_positions():
    center_x = rover_pos[0] + OBSTACLE_DISTANCE * math.cos(math.radians(mast_angle))
    center_y = rover_pos[1] - OBSTACLE_DISTANCE * math.sin(math.radians(mast_angle))
    start_x = center_x - (OBSTACLE_LENGTH / 2) * math.sin(math.radians(mast_angle))
    start_y = center_y - (OBSTACLE_LENGTH / 2) * math.cos(math.radians(mast_angle))
    end_x = center_x + (OBSTACLE_LENGTH / 2) * math.sin(math.radians(mast_angle))
    end_y = center_y + (OBSTACLE_LENGTH / 2) * math.cos(math.radians(mast_angle))
    return [(start_x, start_y), (end_x, end_y)]

def save_map(name=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name}.json" if name else f"{timestamp}_map.json"
    filepath = os.path.join(MAPS_DIR, filename)

    map_data = {
        "path": path,
        "rover_pos": rover_pos,
        "resources": resources,
        "obstacles": obstacles,
    }

    with open(filepath, "w") as f:
        json.dump(map_data, f, indent=4)
    print(f"[DEBUG] Map saved to {filepath}")

def load_map(filepath):
    global path, rover_pos, resources, obstacles

    with open(filepath, "r") as f:
        map_data = json.load(f)

    path = map_data["path"]
    rover_pos = map_data["rover_pos"]
    resources = map_data["resources"]
    obstacles = map_data["obstacles"]
    print(f"[DEBUG] Map loaded from {filepath}")

def list_maps():
    files = [f for f in os.listdir(MAPS_DIR) if f.endswith(".json")]
    for i, file in enumerate(files):
        print(f"{i + 1}: {file}")
    return files

def reset_map():
    global path, rover_pos, resources, obstacles
    path = []
    rover_pos = [WIDTH // 2, HEIGHT // 2]
    resources = []
    obstacles = []
    print("[DEBUG] Map reset.")

def main_menu():
    """Main menu to save or load maps."""
    global auto_save

    while True:
        print("\nMain Menu:")
        print("1. Save current map")
        print("2. Load a saved map")
        print("3. Start with a new map")
        print("4. Toggle auto-save (currently {})".format("ON" if auto_save else "OFF"))
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter a name for the map (optional): ").strip()
            save_map(name)
        elif choice == "2":
            files = list_maps()
            if not files:
                print("No saved maps found.")
                continue
            selection = int(input("Enter the number of the map to load: ")) - 1
            if 0 <= selection < len(files):
                load_map(os.path.join(MAPS_DIR, files[selection]))
                print(f"Map loaded successfully. Starting game...")
                return  # Start game directly after loading
            else:
                print("Invalid selection.")
        elif choice == "3":
            reset_map()
            break  # Proceed to the game with a new map
        elif choice == "4":
            auto_save = not auto_save
            print(f"Auto-save is now {'ON' if auto_save else 'OFF'}.")
        elif choice == "5":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Please try again.")

def main():
    global rover_pos, rover_angle, mast_angle, mast_offset, odometer
    global show_resource_list, show_obstacle_list, place_resource_pressed, place_obstacle_pressed

    main_menu()  # Show the main menu at startup

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        draw_path()
        draw_rover()
        draw_arrows()
        draw_resources()
        draw_obstacles()
        draw_hud()
        draw_lists()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if auto_save:
                    save_map()  # Save the map automatically on exit if enabled
                print("Exiting...")
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    show_resource_list = not show_resource_list
                if event.key == pygame.K_SPACE:
                    show_obstacle_list = not show_obstacle_list
                if event.key == pygame.K_o and not place_resource_pressed:
                    resources.append(compute_resource_position())
                    place_resource_pressed = True
                if event.key == pygame.K_p and not place_obstacle_pressed:
                    obstacles.append(compute_obstacle_positions())
                    place_obstacle_pressed = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_o:
                    place_resource_pressed = False
                if event.key == pygame.K_p:
                    place_obstacle_pressed = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            dx = rover_speed * math.cos(math.radians(rover_angle))
            dy = -rover_speed * math.sin(math.radians(rover_angle))
            rover_pos[0] += dx
            rover_pos[1] += dy
            odometer += math.sqrt(dx**2 + dy**2)
            path.append(tuple(rover_pos))
        if keys[pygame.K_DOWN]:
            dx = -rover_speed * math.cos(math.radians(rover_angle))
            dy = rover_speed * math.sin(math.radians(rover_angle))
            rover_pos[0] += dx
            rover_pos[1] += dy
            odometer += math.sqrt(dx**2 + dy**2)
            path.append(tuple(rover_pos))
        if keys[pygame.K_LEFT]:
            rover_angle += 5
            mast_angle = rover_angle + mast_offset
        if keys[pygame.K_RIGHT]:
            rover_angle -= 5
            mast_angle = rover_angle + mast_offset
        if keys[pygame.K_a]:
            mast_angle += 5
            mast_offset = mast_angle - rover_angle
        if keys[pygame.K_d]:
            mast_angle -= 5
            mast_offset = mast_angle - rover_angle
        if keys[pygame.K_r]:
            mast_offset = 0
            mast_angle = rover_angle

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()