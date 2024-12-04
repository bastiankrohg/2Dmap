import pygame
import math
from components.constants import HUD_FONT_SIZE, WIDTH, HEIGHT

# Fonts
pygame.init()
hud_font = pygame.font.SysFont(None, HUD_FONT_SIZE)
list_font = pygame.font.SysFont(None, 18)

def update_rover_position(keys, rover_pos, rover_angle, path, odometer, mast_angle):
    rover_speed = 5
    if keys[pygame.K_UP]:
        dx = rover_speed * math.cos(math.radians(rover_angle))
        dy = -rover_speed * math.sin(math.radians(rover_angle))
        rover_pos[0] += dx
        rover_pos[1] += dy
        odometer += math.sqrt(dx**2 + dy**2)
        path.append(tuple(rover_pos))
    if keys[pygame.K_DOWN]:
        dx = -rover_speed * math.cos(math.radians(rover_angle))
        dy = rover_speed * math.sin(math.radians(rover_angle))
        rover_pos[0] += dx
        rover_pos[1] += dy
        odometer += math.sqrt(dx**2 + dy**2)
        path.append(tuple(rover_pos))
    if keys[pygame.K_LEFT]:
        rover_angle += 5
        mast_angle += 5  # Keep the relative masthead angle intact
    if keys[pygame.K_RIGHT]:
        rover_angle -= 5
        mast_angle -= 5
    if keys[pygame.K_a]:
        mast_angle += 5
    if keys[pygame.K_d]:
        mast_angle -= 5
    return rover_pos, rover_angle, path, odometer, mast_angle

# HUD and Overlay Drawing Functions
def draw_hud(screen, resources, obstacles, odometer, scanned_percentage):
    """Display the HUD with resource count, obstacle count, odometer, and scanned coverage."""
    resource_count = len(resources) if isinstance(resources, list) else 0
    obstacle_count = len(obstacles) if isinstance(obstacles, list) else 0

    hud_text = (
        f"Resources: {resource_count} | Obstacles: {obstacle_count} | "
        f"Odometer: {odometer:.2f} cm | Scanned: {scanned_percentage:.1f}%"
    )

    hud_surface = hud_font.render(hud_text, True, (255, 255, 255))
    screen.blit(hud_surface, (10, 10))


def draw_overlay(screen, title, items):
    """Draw an overlay list of items with a title."""
    overlay_width = WIDTH // 3
    overlay_height = HEIGHT // 2
    overlay_x = (WIDTH - overlay_width) // 2
    overlay_y = HEIGHT - overlay_height - 10

    pygame.draw.rect(screen, (50, 50, 50), (overlay_x, overlay_y, overlay_width, overlay_height))
    pygame.draw.rect(screen, (255, 255, 255), (overlay_x, overlay_y, overlay_width, overlay_height), 2)

    # Display overlay title
    header_text = list_font.render(title, True, (255, 255, 255))
    screen.blit(header_text, (overlay_x + 10, overlay_y + 10))

    # Display each item in the list
    for i, item in enumerate(items):
        if isinstance(item[0], tuple):  # For obstacles
            start, end = item
            text = f"{i + 1}: ({round(start[0], 2)}, {round(start[1], 2)}) to ({round(end[0], 2)}, {round(end[1], 2)})"
        else:  # For resources
            text = f"{i + 1}: ({round(item[0], 2)}, {round(item[1], 2)})"
        item_surface = list_font.render(text, True, (255, 255, 255))
        screen.blit(item_surface, (overlay_x + 10, overlay_y + 30 + i * 20))

def toggle_hud(event, show_resource_list, show_obstacle_list):
    """Toggle the HUD display for resources and obstacles."""
    if event.key == pygame.K_TAB:
        show_resource_list = not show_resource_list
    if event.key == pygame.K_SPACE:
        show_obstacle_list = not show_obstacle_list
    return show_resource_list, show_obstacle_list
