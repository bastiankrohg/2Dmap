import pygame
import math
import sys

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
RESOURCE_DISTANCE = 15  # Distance to place the resource in front of the mast
OBSTACLE_DISTANCE = 15  # Distance to place the obstacle in front of the mast
OBSTACLE_LENGTH = 30  # Length of the obstacle
HUD_FONT_SIZE = 24

# Screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping with Odometer")
clock = pygame.time.Clock()

# Fonts
hud_font = pygame.font.SysFont(None, HUD_FONT_SIZE)
list_font = pygame.font.SysFont(None, 18)

# Rover attributes
rover_pos = [WIDTH // 2, HEIGHT // 2]
rover_angle = 0  # Rover's facing angle in degrees
mast_angle = 0  # Mast's facing angle in degrees
mast_offset = 0  # Offset between rover_angle and mast_angle
rover_speed = 5
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
    pygame.draw.circle(screen, ROVER_COLOR, (int(rover_pos[0]), int(rover_pos[1])), GRID_SIZE // 2)

def draw_path():
    for pos in path:
        pygame.draw.circle(screen, PATH_COLOR, (int(pos[0]), int(pos[1])), 2)

def draw_arrows():
    # Draw the rover's facing direction
    rover_end_x = rover_pos[0] + math.cos(math.radians(rover_angle)) * 40
    rover_end_y = rover_pos[1] - math.sin(math.radians(rover_angle)) * 40
    pygame.draw.line(screen, ROVER_COLOR, rover_pos, (rover_end_x, rover_end_y), 3)

    # Draw the mast's facing direction
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
    # Display the number of resources, obstacles, and odometer reading
    hud_surface = hud_font.render(
        f"Resources: {len(resources)} | Obstacles: {len(obstacles)} | Odometer: {odometer:.2f} cm",
        True,
        (255, 255, 255),
    )
    screen.blit(hud_surface, (10, 10))

def draw_lists():
    # Display resources and obstacles lists when toggled
    if show_resource_list:
        draw_overlay("Resource List", resources)
    if show_obstacle_list:
        draw_overlay("Obstacle List", obstacles)

def draw_overlay(title, items):
    overlay_width = WIDTH // 3
    overlay_height = HEIGHT // 2
    overlay_x = (WIDTH - overlay_width) // 2
    overlay_y = HEIGHT - overlay_height - 10

    # Draw overlay background
    pygame.draw.rect(screen, (50, 50, 50, 180), (overlay_x, overlay_y, overlay_width, overlay_height))

    # Draw overlay border
    pygame.draw.rect(screen, (255, 255, 255), (overlay_x, overlay_y, overlay_width, overlay_height), 2)

    # Display title
    header_text = list_font.render(title, True, (255, 255, 255))
    screen.blit(header_text, (overlay_x + 10, overlay_y + 10))

    # Display items
    for i, item in enumerate(items):
        if isinstance(item[0], tuple):  # For obstacles (line segments)
            start = item[0]
            end = item[1]
            display_text = f"{i + 1}: ({round(start[0], 2)}, {round(start[1], 2)}) to ({round(end[0], 2)}, {round(end[1], 2)})"
        else:  # For resources (points)
            display_text = f"{i + 1}: ({round(item[0], 2)}, {round(item[1], 2)})"
        
        item_surface = list_font.render(display_text, True, (255, 255, 255))
        screen.blit(item_surface, (overlay_x + 10, overlay_y + 30 + i * 20))

# Placement functions
def compute_resource_position():
    """Compute the position of a resource placed in front of the mast."""
    x = rover_pos[0] + RESOURCE_DISTANCE * math.cos(math.radians(mast_angle))
    y = rover_pos[1] - RESOURCE_DISTANCE * math.sin(math.radians(mast_angle))
    return [x, y]

def compute_obstacle_positions():
    """Compute the start and end positions of an obstacle line in front of the mast."""
    center_x = rover_pos[0] + OBSTACLE_DISTANCE * math.cos(math.radians(mast_angle))
    center_y = rover_pos[1] - OBSTACLE_DISTANCE * math.sin(math.radians(mast_angle))
    start_x = center_x - (OBSTACLE_LENGTH / 2) * math.sin(math.radians(mast_angle))
    start_y = center_y - (OBSTACLE_LENGTH / 2) * math.cos(math.radians(mast_angle))
    end_x = center_x + (OBSTACLE_LENGTH / 2) * math.sin(math.radians(mast_angle))
    end_y = center_y + (OBSTACLE_LENGTH / 2) * math.cos(math.radians(mast_angle))
    return [(start_x, start_y), (end_x, end_y)]

# Main loop
def main():
    global rover_pos, rover_angle, mast_angle, mast_offset, odometer
    global show_resource_list, show_obstacle_list, place_resource_pressed, place_obstacle_pressed

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
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    show_resource_list = not show_resource_list  # Toggle resource list
                if event.key == pygame.K_SPACE:
                    show_obstacle_list = not show_obstacle_list  # Toggle obstacle list
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

        # Movement controls
        if keys[pygame.K_UP]:  # Move forward
            dx = rover_speed * math.cos(math.radians(rover_angle))
            dy = -rover_speed * math.sin(math.radians(rover_angle))
            rover_pos[0] += dx
            rover_pos[1] += dy
            odometer += math.sqrt(dx**2 + dy**2)  # Add distance to odometer
            path.append(tuple(rover_pos))
        if keys[pygame.K_DOWN]:  # Move backward
            dx = -rover_speed * math.cos(math.radians(rover_angle))
            dy = rover_speed * math.sin(math.radians(rover_angle))
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