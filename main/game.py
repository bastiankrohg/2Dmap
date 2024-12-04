import pygame
from components.drawing import (
    draw_grid, draw_path, draw_rover, draw_arrows,
    draw_resources, draw_obstacles, draw_fov, update_scanned_area
)
from components.game_logic import update_rover_position, draw_hud, draw_overlay
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR, SCANNED_OFFSET
from components.utils import compute_scanned_percentage

def game_loop(client, scanned_surface, rover_pos, rover_angle, mast_angle, path, odometer, view_offset):
    """
    Main game loop that handles drawing, updating, and rover movements.
    """
    running = True
    trace_scanned_area = True

    while running:
        screen = pygame.display.get_surface()
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, view_offset)
        draw_path(screen, path, view_offset)
        draw_rover(screen, rover_pos, view_offset)
        draw_arrows(screen, rover_pos, rover_angle, mast_angle, view_offset)
        draw_resources(screen, resources=[], view_offset=view_offset)
        draw_obstacles(screen, obstacles=[], view_offset=view_offset)

        # Update the scanned surface
        if trace_scanned_area:
            update_scanned_area(scanned_surface, rover_pos, mast_angle, view_offset)

        # Blit the scanned area
        screen.blit(
            scanned_surface,
            (0, 0),
            pygame.Rect(
                view_offset[0] + SCANNED_OFFSET[0],
                view_offset[1] + SCANNED_OFFSET[1],
                WIDTH,
                HEIGHT,
            ),
        )

        # Draw the FoV
        draw_fov(screen, rover_pos, mast_angle, view_offset)

        # Adjust view_offset dynamically
        if rover_pos[0] - view_offset[0] < WIDTH // 4:
            view_offset[0] -= WIDTH // 10
        elif rover_pos[0] - view_offset[0] > 3 * WIDTH // 4:
            view_offset[0] += WIDTH // 10
        if rover_pos[1] - view_offset[1] < HEIGHT // 4:
            view_offset[1] -= HEIGHT // 10
        elif rover_pos[1] - view_offset[1] > 3 * HEIGHT // 4:
            view_offset[1] += HEIGHT // 10

        # Simulate user control
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            client.send_drive_forward(10)
            rover_pos[1] -= 10
        elif keys[pygame.K_s]:
            client.send_reverse(10)
            rover_pos[1] += 10
        elif keys[pygame.K_a]:
            client.send_turn_left(15)
            rover_angle -= 15
        elif keys[pygame.K_d]:
            client.send_turn_right(15)
            rover_angle += 15

        scanned_percentage = compute_scanned_percentage(scanned_surface)
        draw_hud(screen, [], [], odometer, scanned_percentage, rover_pos)
        pygame.display.flip()
        pygame.time.Clock().tick(30)