# v1 - simple movement

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
PATH_COLOR = (200, 200, 200)
BACKGROUND_COLOR = (0, 0, 0)

# Screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping with Mast Offset")
clock = pygame.time.Clock()

# Rover attributes
rover_pos = [WIDTH // 2, HEIGHT // 2]
rover_angle = 0  # Rover's facing angle in degrees
mast_angle = 0  # Mast's facing angle in degrees
mast_offset = 0  # Offset between rover_angle and mast_angle
rover_speed = 5
path = []

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

# Main loop
def main():
    global rover_pos, rover_angle, mast_angle, mast_offset
    running = True

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        draw_path()
        draw_rover()
        draw_arrows()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()