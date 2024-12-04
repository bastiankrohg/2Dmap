import pygame
import math
from components.constants import *

def draw_grid(screen, view_offset):
    """Draws a grid on the screen with an offset for the view."""
    grid_color = (50, 50, 50)  # Define the grid color
    grid_spacing = 20  # Define the spacing between grid lines

    # Calculate the start and end points for the grid lines considering the view offset
    start_x = -(view_offset[0] % grid_spacing)
    start_y = -(view_offset[1] % grid_spacing)

    # Draw vertical grid lines
    for x in range(start_x, screen.get_width(), grid_spacing):
        pygame.draw.line(screen, grid_color, (x, 0), (x, screen.get_height()))

    # Draw horizontal grid lines
    for y in range(start_y, screen.get_height(), grid_spacing):
        pygame.draw.line(screen, grid_color, (0, y), (screen.get_width(), y))

def draw_rover(screen, rover_pos, view_offset):
    """Draw the rover at its current position."""
    adjusted_pos = (int(rover_pos[0] - view_offset[0]), int(rover_pos[1] - view_offset[1]))
    pygame.draw.circle(screen, (0, 255, 0), adjusted_pos, 10)

def draw_path(screen, path, view_offset):
    """Draw the path the rover has traveled."""
    for pos in path:
        adjusted_pos = (int(pos[0] - view_offset[0]), int(pos[1] - view_offset[1]))
        pygame.draw.circle(screen, (200, 200, 200), adjusted_pos, 2)

def draw_arrows(screen, rover_pos, rover_angle, mast_angle, view_offset):
    """Draw arrows indicating the rover's and mast's facing direction."""
    adjusted_rover_pos = (rover_pos[0] - view_offset[0], rover_pos[1] - view_offset[1])

    # Rover arrow
    rover_end_x = adjusted_rover_pos[0] + math.cos(math.radians(rover_angle)) * 40
    rover_end_y = adjusted_rover_pos[1] - math.sin(math.radians(rover_angle)) * 40
    pygame.draw.line(screen, (0, 255, 0), adjusted_rover_pos, (rover_end_x, rover_end_y), 3)

    # Mast arrow
    mast_end_x = adjusted_rover_pos[0] + math.cos(math.radians(mast_angle)) * 40
    mast_end_y = adjusted_rover_pos[1] - math.sin(math.radians(mast_angle)) * 40
    pygame.draw.line(screen, (0, 0, 255), adjusted_rover_pos, (mast_end_x, mast_end_y), 3)

def draw_resources(screen, resources, view_offset):
    """Draw all resources on the map."""
    for resource in resources:
        adjusted_pos = (int(resource[0] - view_offset[0]), int(resource[1] - view_offset[1]))
        pygame.draw.circle(screen, (0, 255, 255), adjusted_pos, 5)


def draw_obstacles(screen, obstacles, view_offset):
    """Draw all obstacles on the map."""
    for obstacle in obstacles:
        adjusted_start = (int(obstacle[0][0] - view_offset[0]), int(obstacle[0][1] - view_offset[1]))
        adjusted_end = (int(obstacle[1][0] - view_offset[0]), int(obstacle[1][1] - view_offset[1]))
        pygame.draw.line(screen, (255, 0, 0), adjusted_start, adjusted_end, 3)