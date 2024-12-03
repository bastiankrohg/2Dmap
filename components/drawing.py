import pygame
import math
from components.constants import *

def draw_grid(screen):
    """Draws the grid."""
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))


def draw_rover(screen, rover_pos):
    """Draws the rover."""
    pygame.draw.circle(screen, ROVER_COLOR, (int(rover_pos[0]), int(rover_pos[1])), GRID_SIZE // 2)


def draw_path(screen, path):
    """Draws the path."""
    for pos in path:
        # Validate that pos is a tuple with two numerical values
        if isinstance(pos, tuple) and len(pos) == 2:
            try:
                x, y = int(pos[0]), int(pos[1])
                pygame.draw.circle(screen, PATH_COLOR, (x, y), 2)
            except (ValueError, TypeError):
                print(f"[ERROR] Invalid path coordinate: {pos}")
        else:
            print(f"[ERROR] Skipping invalid path entry: {pos}")


def draw_hud(screen, resources, obstacles, odometer):
    """Draws the HUD with information."""
    font = pygame.font.SysFont(None, HUD_FONT_SIZE)
    hud_surface = font.render(
        f"Resources: {len(resources)} | Obstacles: {len(obstacles)} | Odometer: {odometer:.2f} cm",
        True,
        (255, 255, 255),
    )
    screen.blit(hud_surface, (10, 10))