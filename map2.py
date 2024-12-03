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
PATH_COLOR = (200, 200, 200)
BACKGROUND_COLOR = (0, 0, 0)
RESOURCE_DISTANCE = 15  # Distance to place the resource in front of the mast
HUD_FONT_SIZE = 24

# Screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping with Mast-Based Resource Placement")
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

# Resources
resources = []  # List to store resource positions
show_resource_list = False  # Whether the resource list is displayed

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

def draw_hud():
    # Display the number of resources found
    resource_count_text = f"Resources Found: {len(resources)}"
    hud_surface = hud_font.render(resource_count_text, True, (255, 255, 255))
    screen.blit(hud_surface, (10, 10))

def draw_resource_list():
    # Draw the resource list as an overlay
    overlay_width = WIDTH // 3
    overlay_height = HEIGHT // 2
    overlay_x = (WIDTH - overlay_width) // 2
    overlay_y = HEIGHT - overlay_height - 10

    # Draw overlay background
    pygame.draw.rect(screen, (50, 50, 50, 180), (overlay_x, overlay_y, overlay_width, overlay_height))

    # Draw overlay border
    pygame.draw.rect(screen, (255, 255, 255), (overlay_x, overlay_y, overlay_width, overlay_height), 2)

    # Display resource list
    header_text = list_font.render("Resource List", True, (255, 255, 255))
    screen.blit(header_text, (overlay_x + 10, overlay_y + 10))

    # Display each resource
    for i, resource in enumerate(resources):
        resource_text = f"{i + 1}: ({int(resource[0])}, {int(resource[1])})"
        resource_surface = list_font.render(resource_text, True, (255, 255, 255))
        screen.blit(resource_surface, (overlay_x + 10, overlay_y + 30 + i * 20))

# Function to compute resource placement
def compute_resource_position():
    """Compute the position of a resource placed at a fixed distance in front of the mast."""
    x = rover_pos[0] + RESOURCE_DISTANCE * math.cos(math.radians(mast_angle))
    y = rover_pos[1] - RESOURCE_DISTANCE * math.sin(math.radians(mast_angle))
    return [x, y]

# Main loop
def main():
    global rover_pos, rover_angle, mast_angle, mast_offset, show_resource_list
    running = True

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        draw_path()
        draw_rover()
        draw_arrows()
        draw_resources()
        draw_hud()

        if show_resource_list:
            draw_resource_list()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                show_resource_list = not show_resource_list  # Toggle resource list

        keys = pygame.key.get_pressed()

        # Movement controls
        if keys[pygame.K_UP]:  # Move forward
            rover_pos[0] += rover_speed * math.cos(math.radians(rover_angle))
            rover_pos[1] -= rover_speed * math.sin(math.radians(rover_angle))
            path.append(tuple(rover_pos))
        if keys[pygame.K_DOWN]:  # Move backward
            rover_pos[0] -= rover_speed * math.cos(math.radians(rover_angle))
            rover_pos[1] += rover_speed * math.sin(math.radians(rover_angle))
            path.append(tuple(rover_pos))
        if keys[pygame.K_LEFT]:  # Turn rover left
            rover_angle += 5
            mast_angle = rover_angle + mast_offset  # Maintain mast offset
        if keys[pygame.K_RIGHT]:  # Turn rover right
            rover_angle -= 5
            mast_angle = rover_angle + mast_offset  # Maintain mast offset

        # Mast control
        if keys[pygame.K_a]:  # Rotate mast left
            mast_angle += 5
            mast_offset = mast_angle - rover_angle  # Update mast offset
        if keys[pygame.K_d]:  # Rotate mast right
            mast_angle -= 5
            mast_offset = mast_angle - rover_angle  # Update mast offset
        if keys[pygame.K_r]:  # Reset mast to rover direction
            mast_offset = 0
            mast_angle = rover_angle

        # Place resource
        if keys[pygame.K_o]:  # Press 'O' to place a resource
            resource_pos = compute_resource_position()
            resources.append(resource_pos)
            print(f"[DEBUG] Resource placed at: {resource_pos}")

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()