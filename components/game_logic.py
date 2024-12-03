import pygame
import math

def update_rover_position(keys, rover_pos, rover_angle, path, odometer, mast_angle):
    """Updates rover position, angle, and path based on key presses."""
    speed = 5  # Movement speed in pixels per frame
    turn_speed = 5  # Angle change in degrees per frame

    # Track if movement happened to update path
    moved = False

    # Movement logic
    if keys[pygame.K_UP]:  # Move forward
        rover_pos[0] += speed * math.cos(math.radians(rover_angle))
        rover_pos[1] -= speed * math.sin(math.radians(rover_angle))
        odometer += speed
        moved = True

    if keys[pygame.K_DOWN]:  # Move backward
        rover_pos[0] -= speed * math.cos(math.radians(rover_angle))
        rover_pos[1] += speed * math.sin(math.radians(rover_angle))
        odometer += speed
        moved = True

    if keys[pygame.K_LEFT]:  # Turn left
        rover_angle = (rover_angle - turn_speed) % 360
        moved = True

    if keys[pygame.K_RIGHT]:  # Turn right
        rover_angle = (rover_angle + turn_speed) % 360
        moved = True

    # Adjust mast angle independently
    if keys[pygame.K_a]:  # Rotate mast left
        mast_angle = (mast_angle - turn_speed) % 360

    if keys[pygame.K_d]:  # Rotate mast right
        mast_angle = (mast_angle + turn_speed) % 360

    # Add current position to path if moved
    if moved:
        path.append(rover_pos[:])  # Store a copy of the current position

    return rover_pos, rover_angle, path, odometer, mast_angle