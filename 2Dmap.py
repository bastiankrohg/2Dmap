import argparse
import grpc
import pygame
from concurrent import futures
from rover_protos import mars_rover_pb2, mars_rover_pb2_grpc
from components.map_management import save_map, load_map, get_last_used_map
from components.drawing import (
    draw_grid, draw_path, draw_rover, draw_fov, update_scanned_area
)
from components.game_logic import update_rover_position, draw_hud
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR, MAP_SIZE
from components.utils import compute_resource_position, compute_obstacle_positions

class MappingServer(mars_rover_pb2_grpc.RoverServiceServicer):
    def __init__(self, headless=False):
        self.headless = headless
        self.rover_pos = [0, 0]
        self.rover_angle = 0
        self.mast_angle = 0
        self.mast_offset = 0
        self.path = []
        self.odometer = 0
        self.view_offset = [-WIDTH // 2, -HEIGHT // 2]
        self.resources = []
        self.obstacles = []
        self.scanned_surface = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)
        self.trace_scanned_area = True

        if not self.headless:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Rover Mapping")
            self.clock = pygame.time.Clock()

    def DriveForward(self, request, context):
        self._update_rover_position(speed=request.speed, forward=True)
        return mars_rover_pb2.CommandResponse(success=True, message="Moved forward")

    def Reverse(self, request, context):
        self._update_rover_position(speed=request.speed, forward=False)
        return mars_rover_pb2.CommandResponse(success=True, message="Moved backward")

    def TurnLeft(self, request, context):
        self.rover_angle = (self.rover_angle + request.angle) % 360
        return mars_rover_pb2.CommandResponse(success=True, message="Turned left")

    def TurnRight(self, request, context):
        self.rover_angle = (self.rover_angle - request.angle) % 360
        return mars_rover_pb2.CommandResponse(success=True, message="Turned right")

    def RotatePeriscope(self, request, context):
        self.mast_angle = (self.mast_angle + request.angle) % 360
        return mars_rover_pb2.CommandResponse(success=True, message="Periscope rotated")

    def PlaceResource(self, request, context):
        resource_pos = compute_resource_position(self.rover_pos, self.mast_angle, request.distance)
        self.resources.append(resource_pos)
        return mars_rover_pb2.CommandResponse(success=True, message="Resource placed")

    def PlaceObstacle(self, request, context):
        obstacle_pos = compute_obstacle_positions(self.rover_pos, self.mast_angle, request.distance)
        self.obstacles.append(obstacle_pos)
        return mars_rover_pb2.CommandResponse(success=True, message="Obstacle placed")

    def StopMovement(self, request, context):
        return mars_rover_pb2.CommandResponse(success=True, message="Movement stopped")

    def _update_rover_position(self, speed, forward=True):
        dx = speed * (1 if forward else -1) * pygame.math.Vector2(1, 0).rotate(self.rover_angle).x
        dy = speed * (1 if forward else -1) * pygame.math.Vector2(1, 0).rotate(self.rover_angle).y
        self.rover_pos[0] += dx
        self.rover_pos[1] += dy
        self.path.append(tuple(self.rover_pos))

    def game_loop(self):
        running = True
        while running:
            if not self.headless:
                self.screen.fill(BACKGROUND_COLOR)
                draw_grid(self.screen, self.view_offset)
                draw_path(self.screen, self.path, self.view_offset)
                draw_rover(self.screen, self.rover_pos, self.view_offset)
                draw_fov(self.screen, self.rover_pos, self.mast_angle, self.view_offset)

                # Update scanned area
                if self.trace_scanned_area:
                    update_scanned_area(self.scanned_surface, self.rover_pos, self.mast_angle, self.view_offset)

                # Blit the scanned area
                self.screen.blit(
                    self.scanned_surface,
                    (0, 0),
                    pygame.Rect(
                        self.view_offset[0],
                        self.view_offset[1],
                        WIDTH,
                        HEIGHT,
                    ),
                )

                draw_hud(self.screen, self.resources, self.obstacles, self.odometer, 0, self.rover_pos)
                pygame.display.flip()
                self.clock.tick(30)

            # Exit condition for headless mode
            if self.headless:
                break

    def serve(self, server_address="localhost:50052"):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        mars_rover_pb2_grpc.add_RoverServiceServicer_to_server(self, server)
        server.add_insecure_port(server_address)
        print(f"[DEBUG] gRPC Mapping Server running on {server_address}")
        server.start()
        self.game_loop()
        server.wait_for_termination()


def main():
    parser = argparse.ArgumentParser(description="2D Rover Mapping with gRPC")
    parser.add_argument("--headless", action="store_true", help="Run without GUI")
    args = parser.parse_args()

    mapping_server = MappingServer(headless=args.headless)
    mapping_server.serve()


if __name__ == "__main__":
    main()