import pygame
import sys
from components.map_management import save_map, load_map, get_last_used_map, list_maps
from components.drawing import draw_grid, draw_rover, draw_path, draw_obstacles, draw_resources, draw_arrows
from components.game_logic import update_rover_position, draw_hud, draw_overlay
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR
from components.utils import compute_resource_position, compute_obstacle_positions

# Global variables for game state
rover_pos = [WIDTH // 2, HEIGHT // 2]  # Starting position of the rover
rover_angle = 0  # Rover's facing angle in degrees
mast_angle = 0  # Mast's facing angle in degrees
mast_offset = 0  # Relative angle between rover and mast
path = []  # Path taken by the rover
odometer = 0  # Total distance traveled

resources = []  # List to store resource positions
obstacles = []  # List to store obstacle line segments

show_resource_list = False  # Whether the resource list overlay is displayed
show_obstacle_list = False  # Whether the obstacle list overlay is displayed

# Initialize pygame
pygame.init()

# Screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping Game")
clock = pygame.time.Clock()

def menu_screen():
    """Display the main menu and return the user's selection."""
    screen.fill(BACKGROUND_COLOR)
    font = pygame.font.Font(None, 36)
    options = ["Load Map", "Start New"]
    current_selection = 0  # Initialize the current selection
    selected_map = None
    show_full_list = False

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        title = font.render("Main Menu", True, (255, 255, 255))
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
                            # Logic to handle map list
                            selected_map = list_maps()  # Add dropdown logic here
                            return selected_map, False
                    elif options[current_selection] == "Start New":
                        return "default_map", True
                    
def game_loop():
    global rover_pos, rover_angle, mast_angle, mast_offset, path, odometer
    global resources, obstacles, show_resource_list, show_obstacle_list

    running = True
    place_resource_pressed = False
    place_obstacle_pressed = False

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen)
        draw_path(screen, path)
        draw_rover(screen, rover_pos)
        draw_arrows(screen, rover_pos, rover_angle, mast_angle)
        draw_hud(screen, resources, obstacles, odometer)

        # Draw resources and obstacles
        draw_resources(screen, resources)
        draw_obstacles(screen, obstacles)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_map(resources, obstacles, get_last_used_map() or "default_map")
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    show_resource_list = not show_resource_list
                if event.key == pygame.K_SPACE:
                    show_obstacle_list = not show_obstacle_list
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

        # Draw lists
        if show_resource_list:
            draw_overlay(screen, "Resource List", resources)
        if show_obstacle_list:
            draw_overlay(screen, "Obstacle List", obstacles)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


def main():
    """
    Main entry point for the game, showing the custom menu and starting the game loop.
    """
    map_name, is_new = menu_screen()
    if is_new:
        game_loop()  # Start a new map
    else:
        game_loop(map_name)  # Load an existing map

if __name__ == "__main__":
    main()