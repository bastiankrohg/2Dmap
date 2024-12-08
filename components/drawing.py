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

    # Adjust rover_angle by -90 degrees to align with the expected direction
    # Subtract 180 degrees to reverse the arrow direction
    adjusted_rover_angle = rover_angle - 270
    adjusted_mast_angle = mast_angle - 270

    # Rover arrow
    rover_end_x = adjusted_rover_pos[0] + math.cos(math.radians(adjusted_rover_angle)) * 40
    rover_end_y = adjusted_rover_pos[1] - math.sin(math.radians(adjusted_rover_angle)) * 40
    pygame.draw.line(screen, (0, 255, 0), adjusted_rover_pos, (rover_end_x, rover_end_y), 3)

    # Mast arrow
    # No need to adjust mast_angle; it directly represents the mast's heading
    mast_end_x = adjusted_rover_pos[0] + math.cos(math.radians(adjusted_mast_angle)) * 40
    mast_end_y = adjusted_rover_pos[1] - math.sin(math.radians(adjusted_mast_angle)) * 40
    pygame.draw.line(screen, (0, 0, 255), adjusted_rover_pos, (mast_end_x, mast_end_y), 3)

def draw_fov(screen, rover_pos, mast_angle, view_offset):
    """Draw the circular segment field of view around the rover."""
    adjusted_rover_pos = (
        rover_pos[0] - view_offset[0],
        rover_pos[1] - view_offset[1],
    )

    # Adjust mast angle relative to rover for accurate FoV
    adjusted_mast_angle = mast_angle - 270  # Adjust for expected heading

    # Define the FoV parameters
    start_angle = math.radians(adjusted_mast_angle - FOV_ANGLE // 2)
    end_angle = math.radians(adjusted_mast_angle + FOV_ANGLE // 2)
    radius = FOV_DISTANCE

    # Create a semi-transparent surface
    fov_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    # Draw the arc and fill the segment
    arc_rect = pygame.Rect(
        adjusted_rover_pos[0] - radius,
        adjusted_rover_pos[1] - radius,
        2 * radius,
        2 * radius,
    )

    # Draw the filled circular segment
    points = [adjusted_rover_pos]  # Start at the center
    for angle in range(int(adjusted_mast_angle - FOV_ANGLE // 2), int(adjusted_mast_angle + FOV_ANGLE // 2) + 1):
        x = adjusted_rover_pos[0] + radius * math.cos(math.radians(angle))
        y = adjusted_rover_pos[1] - radius * math.sin(math.radians(angle))
        points.append((x, y))

    # Draw the filled polygon
    pygame.draw.polygon(fov_surface, (255, 255, 0, 50), points)

    # Blit the semi-transparent surface onto the main screen
    screen.blit(fov_surface, (0, 0))


def update_scanned_area(scanned_surface, rover_pos, mast_angle, view_offset):
    """
    Update the scanned area on the global scanned_surface, constrained to the FoV,
    and ensure alignment with the viewport using view_offset.
    """
    # Convert rover_pos to map-relative coordinates
    map_x = int(rover_pos[0] + SCANNED_OFFSET[0])
    map_y = int(rover_pos[1] + SCANNED_OFFSET[1])

    # Scanned area parameters
    scan_radius = FOV_DISTANCE  # Radius of the scanned area
    angle_span = FOV_ANGLE      # Field of view in degrees

    # Create a mask for the scanned area
    for angle in range(-angle_span // 2, angle_span // 2 + 1):
        radians = math.radians(mast_angle + angle)
        end_x = map_x + int(scan_radius * math.cos(radians))
        end_y = map_y - int(scan_radius * math.sin(radians))

        # Draw on the scanned surface only if within bounds
        if 0 <= end_x < scanned_surface.get_width() and 0 <= end_y < scanned_surface.get_height():
            pygame.draw.line(scanned_surface, (128, 128, 128, 50), (map_x, map_y), (end_x, end_y), 1)

    # Debugging output
    # print(f"Rover Global Position: {rover_pos}")
    # print(f"Adjusted Map Position: ({map_x}, {map_y})")
    # print(f"View Offset: {view_offset}")

def draw_resources(screen, resources, view_offset):
    """
    Draw resources on the map. Each resource is represented as a green rectangle
    with an optional label and size.
    """
    for resource in resources:
        position = resource["position"]
        size = int(resource["size"])  # Ensure size is an integer
        label = resource.get("object", "Resource")  # Default label if not provided
        adjusted_start = (position[0] - view_offset[0], position[1] - view_offset[1])

        # Draw the resource as a rectangle
        pygame.draw.rect(screen, (0, 255, 0), (adjusted_start[0], adjusted_start[1], size, size))

        # Draw the label text near the resource
        font = pygame.font.SysFont(None, 24)
        label_surface = font.render(label, True, (255, 255, 255))
        screen.blit(label_surface, (adjusted_start[0] + size + 5, adjusted_start[1]))

def draw_obstacles(screen, obstacles, view_offset):
    """
    Draw obstacles on the map. Each obstacle is represented as a red line
    with an optional label and size defining its length.
    """
    for obstacle in obstacles:
        position = obstacle["position"]
        size = int(obstacle["size"])  # Ensure size is an integer
        label = obstacle.get("object", "Obstacle")  # Default label if not provided
        adjusted_start = (position[0] - view_offset[0], position[1] - view_offset[1])

        # Calculate the end position of the line based on size (length)
        adjusted_end = (adjusted_start[0] + size, adjusted_start[1])

        # Draw the obstacle as a red line
        pygame.draw.line(screen, (255, 0, 0), adjusted_start, adjusted_end, 2)

        # Draw the label text near the obstacle
        font = pygame.font.SysFont(None, 24)
        label_surface = font.render(label, True, (255, 255, 255))
        screen.blit(label_surface, (adjusted_end[0] + 5, adjusted_end[1] - 10))
        