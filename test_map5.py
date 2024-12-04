# v5 - Debugging and functional fixes

import sys
import os
import pygame
import math
from components.drawing import (
    draw_grid,
    draw_rover,
    draw_path,
    draw_arrows,
    draw_resources,
    draw_obstacles,
)
from components.game_logic import (
    draw_overlay,
    draw_hud,
    toggle_hud,
)
from components.map_management import save_map, load_map, reset_map, list_maps
from components.constants import *
from components.utils import compute_resource_position, compute_obstacle_positions


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping")
clock = pygame.time.Clock()


def main():
    global show_resource_list, show_obstacle_list, place_resource_pressed, place_obstacle_pressed

    # Initialize variables
    path, rover_pos, resources, obstacles = reset_map()
    rover_angle = 0
    mast_angle = 0
    mast_offset = 0
    odometer = 0
    auto_save = True
    show_resource_list = False
    show_obstacle_list = False
    place_resource_pressed = False
    place_obstacle_pressed = False

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen)
        draw_path(screen, path)
        draw_rover(screen, rover_pos)
        draw_arrows(screen, rover_pos, rover_angle, mast_angle)
        draw_resources(screen, resources)
        draw_obstacles(screen, obstacles)

        # Draw HUD and lists
        if show_resource_list or show_obstacle_list:
            draw_hud(screen, resources, obstacles, odometer)

        if show_resource_list:
            draw_overlay(screen, "Resource List", resources)
        if show_obstacle_list:
            draw_overlay(screen, "Obstacle List", obstacles)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if auto_save:
                    save_map(path, rover_pos, resources, obstacles, "default_map")
                print("[DEBUG] Quit event detected.")
                running = False

            # Keydown events for toggling HUD and placing resources/obstacles
            if event.type == pygame.KEYDOWN:
                show_resource_list, show_obstacle_list = toggle_hud(event, show_resource_list, show_obstacle_list)
                if event.key == pygame.K_TAB:
                    show_resource_list = not show_resource_list
                elif event.key == pygame.K_SPACE:
                    show_obstacle_list = not show_obstacle_list
                if event.key == pygame.K_o and not place_resource_pressed:
                    resources.append(compute_resource_position(rover_pos, mast_angle))
                    place_resource_pressed = True
                elif event.key == pygame.K_p and not place_obstacle_pressed:
                    obstacles.append(compute_obstacle_positions(rover_pos, mast_angle))
                    place_obstacle_pressed = True

            # Keyup events to release resource/obstacle placement flags
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_o:
                    place_resource_pressed = False
                elif event.key == pygame.K_p:
                    place_obstacle_pressed = False

        # Key state handling for movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            dx = ROVER_SPEED * math.cos(math.radians(rover_angle))
            dy = -ROVER_SPEED * math.sin(math.radians(rover_angle))
            rover_pos[0] += dx
            rover_pos[1] += dy
            odometer += math.sqrt(dx**2 + dy**2)
            path.append(tuple(rover_pos))
        if keys[pygame.K_DOWN]:
            dx = -ROVER_SPEED * math.cos(math.radians(rover_angle))
            dy = ROVER_SPEED * math.sin(math.radians(rover_angle))
            rover_pos[0] += dx
            rover_pos[1] += dy
            odometer += math.sqrt(dx**2 + dy**2)
            path.append(tuple(rover_pos))
        if keys[pygame.K_LEFT]:
            rover_angle += 5
            mast_angle = rover_angle + mast_offset
        if keys[pygame.K_RIGHT]:
            rover_angle -= 5
            mast_angle = rover_angle + mast_offset
        if keys[pygame.K_a]:
            mast_angle += 5
            mast_offset = mast_angle - rover_angle
        if keys[pygame.K_d]:
            mast_angle -= 5
            mast_offset = mast_angle - rover_angle

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()