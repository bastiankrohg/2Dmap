import pygame
import math
from components.constants import *

def draw_grid(screen):
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))

def draw_rover(screen, rover_pos):
    pygame.draw.circle(screen, ROVER_COLOR, (int(rover_pos[0]), int(rover_pos[1])), GRID_SIZE // 2)

def draw_path(screen, path):
    for pos in path:
        pygame.draw.circle(screen, PATH_COLOR, (int(pos[0]), int(pos[1])), 2)

def draw_arrows(screen, rover_pos, rover_angle, mast_angle):
    rover_end_x = rover_pos[0] + math.cos(math.radians(rover_angle)) * 40
    rover_end_y = rover_pos[1] - math.sin(math.radians(rover_angle)) * 40
    pygame.draw.line(screen, ROVER_COLOR, rover_pos, (rover_end_x, rover_end_y), 3)

    mast_end_x = rover_pos[0] + math.cos(math.radians(mast_angle)) * 40
    mast_end_y = rover_pos[1] - math.sin(math.radians(mast_angle)) * 40
    pygame.draw.line(screen, MAST_COLOR, rover_pos, (mast_end_x, mast_end_y), 3)

def draw_resources(screen, resources):
    for resource in resources:
        pygame.draw.circle(screen, RESOURCE_COLOR, (int(resource[0]), int(resource[1])), GRID_SIZE // 4)

def draw_obstacles(screen, obstacles):
    for obstacle in obstacles:
        pygame.draw.line(screen, OBSTACLE_COLOR, obstacle[0], obstacle[1], 3)

