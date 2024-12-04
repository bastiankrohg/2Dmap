# v9.1 - Fixed Scanned Zone Tracing to Map Coordinates

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
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR, SCANNED_OFFSET, MAP_SIZE
from components.utils import compute_resource_position, compute_obstacle_positions, compute_scanned_percentage

# Global variables for game state
# rover_pos = [WIDTH // 2, HEIGHT // 2]
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
view_offset = [0, 0]
dragging = False
drag_start = None

# Map surface dimensions (static)
MAP_WIDTH, MAP_HEIGHT = 2000, 2000

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping Game - Fixed Scanned Zone")
clock = pygame.time.Clock()

# Create the expanded scanned_surface
scanned_surface = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)

# In game_loop, after initializing the scanned_surface
print(f"Scanned surface size: {scanned_surface.get_width()}x{scanned_surface.get_height()}")
print(f"Scanned offset: {SCANNED_OFFSET}")

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
    global resources, obstacles, show_resource_list, show_obstacle_list, view_offset, dragging, drag_start

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

        # Calculate the blitting area based on the viewport and SCANNED_OFFSET
        blit_area = pygame.Rect(
            SCANNED_OFFSET[0] + view_offset[0],
            SCANNED_OFFSET[1] + view_offset[1],
            WIDTH,
            HEIGHT,
        )
        # Blit the appropriate portion of the scanned surface onto the main screen
        screen.blit(scanned_surface, (0, 0), blit_area)


        draw_grid(screen, [int(view_offset[0]), int(view_offset[1])])
        draw_path(screen, path, [int(view_offset[0]), int(view_offset[1])])
        draw_rover(screen, rover_pos, [int(view_offset[0]), int(view_offset[1])])
        draw_arrows(screen, rover_pos, rover_angle, mast_angle, [int(view_offset[0]), int(view_offset[1])])
        draw_resources(screen, resources, [int(view_offset[0]), int(view_offset[1])])
        draw_obstacles(screen, obstacles, [int(view_offset[0]), int(view_offset[1])])

        # Draw the field of view
        draw_fov(screen, rover_pos, mast_angle, [int(view_offset[0]), int(view_offset[1])])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_map(path, rover_pos, resources, obstacles, rover_angle, mast_angle, map_name or "map.json")
                running = False

            # Mouse dragging
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    drag_start = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                dx = event.pos[0] - drag_start[0]
                dy = event.pos[1] - drag_start[1]
                view_offset[0] -= dx
                view_offset[1] -= dy
                drag_start = event.pos

            # Keyboard controls
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

        # Update scanned area (static to map coordinates)
        if trace_scanned_area:
            update_scanned_area(scanned_surface, rover_pos, mast_angle, view_offset)
        
        scanned_percentage = compute_scanned_percentage(scanned_surface)

        # Dynamic viewport adjustment
        margin = 100
        # Adjust view_offset dynamically based on rover's position
        if rover_pos[0] - view_offset[0] < WIDTH // 4:  # Left edge
            view_offset[0] = rover_pos[0] - WIDTH // 4
        if rover_pos[1] - view_offset[1] < HEIGHT // 4:  # Top edge
            view_offset[1] = rover_pos[1] - HEIGHT // 4
        if rover_pos[0] - view_offset[0] > 3 * WIDTH // 4:  # Right edge
            view_offset[0] = rover_pos[0] - 3 * WIDTH // 4
        if rover_pos[1] - view_offset[1] > 3 * HEIGHT // 4:  # Bottom edge
            view_offset[1] = rover_pos[1] - 3 * HEIGHT // 4

        # Draw overlays
        if show_resource_list:
            draw_overlay(screen, "Resource List", resources)
        if show_obstacle_list:
            draw_overlay(screen, "Obstacle List", obstacles)

        draw_hud(screen, resources, obstacles, odometer, scanned_percentage, rover_pos)  

        # print(f"Rover Global Position: {rover_pos}")
        # print(f"View Offset: {view_offset}")
        # print(f"SCANNED_OFFSET: {SCANNED_OFFSET}")
        # print(f"Blitting Area: {blit_area}")

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