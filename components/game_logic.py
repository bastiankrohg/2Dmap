import pygame
import math

def update_rover_position(keys, rover_pos, rover_angle, path, odometer, mast_angle):
    SPEED = 5
    TURN_ANGLE = 5

    if keys[pygame.K_w]:
        rover_pos[0] += SPEED * math.cos(math.radians(rover_angle))
        rover_pos[1] -= SPEED * math.sin(math.radians(rover_angle))
        odometer += SPEED

    if keys[pygame.K_s]:
        rover_pos[0] -= SPEED * math.cos(math.radians(rover_angle))
        rover_pos[1] += SPEED * math.sin(math.radians(rover_angle))
        odometer += SPEED

    if keys[pygame.K_a]:
        rover_angle += TURN_ANGLE

    if keys[pygame.K_d]:
        rover_angle -= TURN_ANGLE

    if keys[pygame.K_q]:
        mast_angle += TURN_ANGLE

    if keys[pygame.K_e]:
        mast_angle -= TURN_ANGLE

    # Ensure only valid numerical data is appended to path
    if keys[pygame.K_w] or keys[pygame.K_s]:
        if isinstance(rover_pos[0], (int, float)) and isinstance(rover_pos[1], (int, float)):
            path.append(tuple(rover_pos))

    return rover_pos, rover_angle, path, odometer, mast_angle