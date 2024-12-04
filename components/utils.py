import math
import numpy as np
import pygame

def compute_resource_position(rover_pos, mast_angle, resource_distance=15):
    """
    Computes the position of a resource relative to the rover's position and mast angle.
    Args:
        rover_pos (list): The current position of the rover [x, y].
        mast_angle (float): The current mast angle in degrees.
        resource_distance (float): Distance from the rover to place the resource.
    Returns:
        list: The computed position of the resource [x, y].
    """
    x = rover_pos[0] + resource_distance * math.cos(math.radians(mast_angle))
    y = rover_pos[1] - resource_distance * math.sin(math.radians(mast_angle))
    return [x, y]


def compute_obstacle_positions(rover_pos, mast_angle, obstacle_distance=15, obstacle_length=30):
    """
    Computes the start and end positions of an obstacle relative to the rover's position and mast angle.
    Args:
        rover_pos (list): The current position of the rover [x, y].
        mast_angle (float): The current mast angle in degrees.
        obstacle_distance (float): Distance from the rover to the center of the obstacle.
        obstacle_length (float): Length of the obstacle.
    Returns:
        list of tuples: The start and end positions of the obstacle [(x1, y1), (x2, y2)].
    """
    # Center of the obstacle
    center_x = rover_pos[0] + obstacle_distance * math.cos(math.radians(mast_angle))
    center_y = rover_pos[1] - obstacle_distance * math.sin(math.radians(mast_angle))
    
    # Start and end positions of the obstacle
    start_x = center_x - (obstacle_length / 2) * math.sin(math.radians(mast_angle))
    start_y = center_y - (obstacle_length / 2) * math.cos(math.radians(mast_angle))
    end_x = center_x + (obstacle_length / 2) * math.sin(math.radians(mast_angle))
    end_y = center_y + (obstacle_length / 2) * math.cos(math.radians(mast_angle))
    
    return [(start_x, start_y), (end_x, end_y)]

def compute_scanned_percentage(scanned_surface):
    """Calculate the percentage of the scanned area."""
    surface_array = pygame.surfarray.pixels_alpha(scanned_surface)
    scanned_pixels = np.count_nonzero(surface_array > 0)  # Non-zero alpha pixels
    total_pixels = surface_array.size
    return (scanned_pixels / total_pixels) * 100