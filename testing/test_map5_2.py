import pygame
import math
import sys
from components.constants import WIDTH, HEIGHT, GRID_SIZE, HUD_FONT_SIZE
from components.utils import compute_resource_position, compute_obstacle_positions
from components.game_logic import draw_hud, draw_overlay, toggle_hud

# Initialize pygame
pygame.init()

# Screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping with HUD and Lists")
clock = pygame.time.Clock()

# Fonts
hud_font = pygame.font.SysFont(None, HUD_FONT_SIZE)
list_font = pygame.font.SysFont(None, 18)

# Rover attributes
rover_pos = [WIDTH // 2, HEIGHT // 2]
rover_angle = 0  # Rover's facing angle in degrees
mast_angle = 0  # Mast's facing angle in degrees
mast_offset = 0  # Offset between rover_angle and mast_angle
path = []
odometer = 0  # Total distance traveled by the rover

# Resources and Obstacles
resources = []  # List to store resource positions
obstacles = []  # List to store obstacle line segments
show_resource_list = False  # Whether the resource list is displayed
show_obstacle_list = False  # Whether the obstacle list is displayed
place_resource_pressed = False  # Debounce flag for resources
place_obstacle_pressed = False  # Debounce flag for obstacles

# Utility functions
def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))

def draw_rover():
    pygame.draw.circle(screen, (0, 255, 0), (int(rover_pos[0]), int(rover_pos[1])), GRID_SIZE // 2)

def draw_path():
    for pos in path:
        pygame.draw.circle(screen, (200, 200, 200), (int(pos[0]), int(pos[1])), 2)

def draw_arrows():
    # Draw the rover's facing direction
    rover_end_x = rover_pos[0] + math.cos(math.radians(rover_angle)) * 40
    rover_end_y = rover_pos[1] - math.sin(math.radians(rover_angle)) * 40
    pygame.draw.line(screen, (0, 255, 0), rover_pos, (rover_end_x, rover_end_y), 3)

    # Draw the mast's facing direction
    mast_end_x = rover_pos[0] + math.cos(math.radians(mast_angle)) * 40
    mast_end_y = rover_pos[1] - math.sin(math.radians(mast_angle)) * 40
    pygame.draw.line(screen, (0, 0, 255), rover_pos, (mast_end_x, mast_end_y), 3)

def draw_resources():
    for resource in resources:
        pygame.draw.circle(screen, (0, 255, 255), (int(resource[0]), int(resource[1])), GRID_SIZE // 4)

def draw_obstacles():
    for obstacle in obstacles:
        pygame.draw.line(screen, (255, 0, 0), obstacle[0], obstacle[1], 3)

# Main loop
def main():
    global rover_pos, rover_angle, mast_angle, mast_offset, odometer
    global show_resource_list, show_obstacle_list, place_resource_pressed, place_obstacle_pressed

    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_grid()
        draw_path()
        draw_rover()
        draw_arrows()
        draw_resources()
        draw_obstacles()
        draw_hud(screen, resources, obstacles, odometer)
        if show_resource_list:
            draw_overlay(screen, "Resource List", resources)
        if show_obstacle_list:
            draw_overlay(screen, "Obstacle List", obstacles)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                show_resource_list, show_obstacle_list = toggle_hud(event, show_resource_list, show_obstacle_list)
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

        keys = pygame.key.get_pressed()

        # Movement controls
        if keys[pygame.K_UP]:  # Move forward
            dx = 5 * math.cos(math.radians(rover_angle))
            dy = -5 * math.sin(math.radians(rover_angle))
            rover_pos[0] += dx
            rover_pos[1] += dy
            odometer += math.sqrt(dx**2 + dy**2)  # Add distance to odometer
            path.append(tuple(rover_pos))
        if keys[pygame.K_DOWN]:  # Move backward
            dx = -5 * math.cos(math.radians(rover_angle))
            dy = 5 * math.sin(math.radians(rover_angle))
            rover_pos[0] += dx
            rover_pos[1] += dy
            odometer += math.sqrt(dx**2 + dy**2)  # Add distance to odometer
            path.append(tuple(rover_pos))
        if keys[pygame.K_LEFT]:  # Turn left
            rover_angle += 5
            mast_angle = rover_angle + mast_offset
        if keys[pygame.K_RIGHT]:  # Turn right
            rover_angle -= 5
            mast_angle = rover_angle + mast_offset
        if keys[pygame.K_a]:  # Mast left
            mast_angle += 5
            mast_offset = mast_angle - rover_angle
        if keys[pygame.K_d]:  # Mast right
            mast_angle -= 5
            mast_offset = mast_angle - rover_angle
        if keys[pygame.K_r]:  # Reset mast
            mast_offset = 0
            mast_angle = rover_angle

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    