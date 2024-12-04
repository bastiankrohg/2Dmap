import pygame
import grpc
import sys
from concurrent import futures
from rover_protos import mars_rover_pb2, mars_rover_pb2_grpc
from components.map_management import save_map, load_map, get_last_used_map, list_maps
from components.drawing import (
    draw_grid,
    draw_path,
    draw_rover,
    draw_arrows,
    draw_resources,
    draw_obstacles,
    draw_fov,
    update_scanned_area,
)
from components.game_logic import update_rover_position, draw_hud, draw_overlay
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR, MAP_SIZE, SCANNED_OFFSET
from components.utils import compute_resource_position, compute_obstacle_positions, compute_scanned_percentage

# Initialize global state
rover_pos = [0, 0]
rover_angle = 0
mast_angle = 0
path = []
odometer = 0
resources = []
obstacles = []
view_offset = [-WIDTH // 2, -HEIGHT // 2]
scanned_surface = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rover Mapping Client")
clock = pygame.time.Clock()


class MappingClient:
    def __init__(self, server_address):
        print("[DEBUG] Connecting to rover server...")
        self.channel = grpc.insecure_channel(server_address)
        self.stub = mars_rover_pb2_grpc.RoverServiceStub(self.channel)
        print("[DEBUG] Connected to rover server.")

    def send_drive_forward(self, speed):
        return self.stub.DriveForward(mars_rover_pb2.DriveRequest(speed=speed))

    def send_reverse(self, speed):
        return self.stub.Reverse(mars_rover_pb2.DriveRequest(speed=speed))

    def send_turn_left(self, angle):
        return self.stub.TurnLeft(mars_rover_pb2.TurnRequest(angle=angle))

    def send_turn_right(self, angle):
        return self.stub.TurnRight(mars_rover_pb2.TurnRequest(angle=angle))

    def send_stop(self):
        return self.stub.StopMovement(mars_rover_pb2.StopRequest())

    def rotate_mast(self, angle):
        return self.stub.RotatePeriscope(mars_rover_pb2.RotateRequest(angle=angle))


def game_loop(client):
    global rover_pos, rover_angle, mast_angle, path, odometer
    global resources, obstacles, view_offset, scanned_surface

    running = True
    trace_scanned_area = True

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, view_offset)
        draw_path(screen, path, view_offset)
        draw_rover(screen, rover_pos, view_offset)
        draw_arrows(screen, rover_pos, rover_angle, mast_angle, view_offset)
        draw_resources(screen, resources, view_offset)
        draw_obstacles(screen, obstacles, view_offset)

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

        # Handle events and gRPC commands
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            client.send_drive_forward(10)
            rover_pos[1] -= 10  # Simulated forward movement
        elif keys[pygame.K_s]:
            client.send_reverse(10)
            rover_pos[1] += 10  # Simulated reverse movement
        elif keys[pygame.K_a]:
            client.send_turn_left(15)
            rover_angle -= 15  # Simulated left turn
        elif keys[pygame.K_d]:
            client.send_turn_right(15)
            rover_angle += 15  # Simulated right turn
        elif keys[pygame.K_SPACE]:
            client.send_stop()

        # Adjust view_offset if the rover moves close to the edges of the viewport
        if rover_pos[0] - view_offset[0] < WIDTH // 4:  # Left boundary
            view_offset[0] -= WIDTH // 10
        elif rover_pos[0] - view_offset[0] > 3 * WIDTH // 4:  # Right boundary
            view_offset[0] += WIDTH // 10
        if rover_pos[1] - view_offset[1] < HEIGHT // 4:  # Top boundary
            view_offset[1] -= HEIGHT // 10
        elif rover_pos[1] - view_offset[1] > 3 * HEIGHT // 4:  # Bottom boundary
            view_offset[1] += HEIGHT // 10

        # Calculate scanned percentage
        scanned_percentage = compute_scanned_percentage(scanned_surface)

        # Draw HUD and overlays
        draw_hud(screen, resources, obstacles, odometer, scanned_percentage, rover_pos)
        pygame.display.flip()
        clock.tick(30)


def main():
    client = MappingClient("localhost:50051")
    print("[DEBUG] Starting mapping client game loop...")
    game_loop(client)


if __name__ == "__main__":
    main()