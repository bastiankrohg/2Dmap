# map9.py - Rover Mapping Game with Scanned Zone Saving and Loading

import pygame
import sys
from components.map_management import save_map, load_map, get_last_used_map, list_maps
from components.drawing import (
    draw_grid,
    draw_path,
    draw_rover,
    draw_arrows,
    draw_resources,
    draw_obstacles,
    draw_fov,
    update_scanned_area,
)
from components.game_logic import update_rover_position, draw_hud, draw_overlay
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR, MAP_SIZE, SCANNED_OFFSET
from components.utils import compute_resource_position, compute_obstacle_positions, compute_scanned_percentage

# Global variables for game state
rover_pos = [0, 0]
rover_angle = 0
mast_angle = 0
mast_offset = 0
path = []
odometer = 0
resources = []
obstacles = []
show_resource_list = False
show_obstacle_list = False

# New variables for dynamic view and dragging
view_offset = [-WIDTH // 2, -HEIGHT // 2]  # Start with the viewport centered on (0, 0)
dragging = False
drag_start = None

# Scanned surface (stored outside game_loop for saving/loading)
scanned_surface = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping Game")
clock = pygame.time.Clock()


def menu_screen():
    """Display the main menu and return the user's selection."""
    screen.fill(BACKGROUND_COLOR)
    font = pygame.font.Font(None, 36)
    options = ["Load Map", "Start New"]
    current_selection = 0
    selected_map = None
    show_full_list = False

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        title = font.render("Rover Map", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        for i, option in enumerate(options):
            color = (255, 255, 255) if i == current_selection else (150, 150, 150)
            text = font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    current_selection = (current_selection + 1) % len(options)
                elif event.key == pygame.K_UP:
                    current_selection = (current_selection - 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[current_selection] == "Load Map":
                        if not show_full_list:
                            last_map = get_last_used_map()
                            if last_map:
                                return last_map, False
                            else:
                                show_full_list = True
                        else:
                            available_maps = list_maps()
                            if available_maps:
                                selected_map = available_maps[0]
                                return selected_map, False
                            else:
                                print("[ERROR] No maps available.")
                                return None, False
                    elif options[current_selection] == "Start New":
                        return "map.json", True
                pygame.event.clear(pygame.KEYDOWN)


def game_loop(map_name=None):
    global rover_pos, rover_angle, mast_angle, mast_offset, path, odometer
    global resources, obstacles, show_resource_list, show_obstacle_list, view_offset, scanned_surface

    if map_name:
        loaded_data = load_map(map_name)
        if loaded_data:
            path = loaded_data["path"]
            rover_pos = loaded_data["rover_pos"]
            resources = loaded_data["resources"]
            obstacles = loaded_data["obstacles"]
            rover_angle = loaded_data["rover_angle"]
            mast_angle = loaded_data["mast_angle"]
            mast_offset = mast_angle - rover_angle
            odometer = 0

            # Load scanned_surface if present
            if "scanned_surface" in loaded_data:
                scanned_surface = pygame.image.load(loaded_data["scanned_surface"]).convert_alpha()
        else:
            print(f"[ERROR] Failed to load map '{map_name}'. Starting a new map.")
            path, resources, obstacles = [], [], []
            rover_pos, rover_angle, mast_angle = [WIDTH // 2, HEIGHT // 2], 0, 0
            odometer = 0

    running = True
    place_resource_pressed = False
    place_obstacle_pressed = False
    trace_scanned_area = False  # Toggle for tracing scanned areas

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, view_offset)
        draw_path(screen, path, view_offset)
        draw_rover(screen, rover_pos, view_offset)
        draw_arrows(screen, rover_pos, rover_angle, mast_angle, view_offset)
        draw_resources(screen, resources, view_offset)
        draw_obstacles(screen, obstacles, view_offset)

        # Update the scanned surface
        if trace_scanned_area:
            update_scanned_area(scanned_surface, rover_pos, mast_angle, view_offset)

        # Blit the scanned area
        screen.blit(
            scanned_surface,
            (0, 0),
            pygame.Rect(
                view_offset[0] + SCANNED_OFFSET[0], 
                view_offset[1] + SCANNED_OFFSET[1], 
                WIDTH, 
                HEIGHT
            ),
        )

        # Draw the FoV
        draw_fov(screen, rover_pos, mast_angle, view_offset)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_map(
                    path, rover_pos, resources, obstacles, rover_angle, mast_angle,
                    map_name or "map.json", scanned_surface
                )
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    show_resource_list = not show_resource_list
                if event.key == pygame.K_SPACE:
                    show_obstacle_list = not show_obstacle_list
                if event.key == pygame.K_s:  # Toggle scanning
                    trace_scanned_area = not trace_scanned_area
                if event.key == pygame.K_o and not place_resource_pressed:
                    resources.append(compute_resource_position(rover_pos, mast_angle))
                    place_resource_pressed = True
                if event.key == pygame.K_p and not place_obstacle_pressed:
                    obstacles.append(compute_obstacle_positions(rover_pos, mast_angle))
                    place_obstacle_pressed = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_o:
                    place_resource_pressed = False
                if event.key == pygame.K_p:
                    place_obstacle_pressed = False

        # Update rover position
        keys = pygame.key.get_pressed()
        rover_pos, rover_angle, path, odometer, mast_angle = update_rover_position(
            keys, rover_pos, rover_angle, path, odometer, mast_angle
        )

        # Adjust view_offset if the rover moves close to the edges of the viewport
        if rover_pos[0] - view_offset[0] < WIDTH // 4:  # Left boundary
            view_offset[0] -= WIDTH // 10
        elif rover_pos[0] - view_offset[0] > 3 * WIDTH // 4:  # Right boundary
            view_offset[0] += WIDTH // 10

        if rover_pos[1] - view_offset[1] < HEIGHT // 4:  # Top boundary
            view_offset[1] -= HEIGHT // 10
        elif rover_pos[1] - view_offset[1] > 3 * HEIGHT // 4:  # Bottom boundary
            view_offset[1] += HEIGHT // 10
            
        # Calculate scanned percentage
        scanned_percentage = compute_scanned_percentage(scanned_surface)

        # Draw lists
        if show_resource_list:
            draw_overlay(screen, "Resource List", resources)
        if show_obstacle_list:
            draw_overlay(screen, "Obstacle List", obstacles)

        draw_hud(screen, resources, obstacles, odometer, scanned_percentage, rover_pos)

        # Update display
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


def main():
    map_name, is_new = menu_screen()
    if is_new:
        game_loop()  # Start a new map
    else:
        game_loop(map_name)  # Load an existing map


if __name__ == "__main__":
    main()