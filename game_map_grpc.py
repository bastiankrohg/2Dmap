import argparse
import grpc
import pygame
import math
from concurrent import futures
from rover_protos import mars_rover_pb2, mars_rover_pb2_grpc
from components.map_management import save_map, load_map, get_last_used_map
from components.drawing import draw_grid, draw_path, draw_rover, draw_arrows, draw_fov, update_scanned_area
from components.game_logic import draw_hud
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR, MAP_SIZE, SCANNED_OFFSET

class MappingServer(mars_rover_pb2_grpc.RoverServiceServicer):
    def __init__(self):
        self.command = None
        self.rover_pos = [WIDTH // 2, HEIGHT // 2]
        self.rover_angle = 0
        self.mast_angle = 0
        self.path = []
        self.trace_scanned_area = False
        print("[DEBUG] MappingServer initialized.")

    def DriveForward(self, request, context):
        self.command = "DriveForward"
        rad_angle = math.radians(self.rover_angle)
        dx = -request.speed * math.sin(rad_angle)
        dy = -request.speed * math.cos(rad_angle)
        self.rover_pos[0] += dx
        self.rover_pos[1] += dy
        self._update_path()
        return mars_rover_pb2.CommandResponse(success=True, message="Moved forward.")

    def Reverse(self, request, context):
        self.command = "Reverse"
        rad_angle = math.radians(self.rover_angle)
        dx = request.speed * math.sin(rad_angle)
        dy = request.speed * math.cos(rad_angle)
        self.rover_pos[0] += dx
        self.rover_pos[1] += dy
        self._update_path()
        return mars_rover_pb2.CommandResponse(success=True, message="Reversed.")

    def TurnLeft(self, request, context):
        self.command = "TurnLeft"
        self.rover_angle -= request.angle
        self.rover_angle %= 360  # Keep angle within bounds
        print(f"[DEBUG] Turned left by {request.angle} degrees.")
        return mars_rover_pb2.CommandResponse(success=True, message="Turned left.")

    def TurnRight(self, request, context):
        self.command = "TurnRight"
        self.rover_angle += request.angle
        self.rover_angle %= 360  # Keep angle within bounds
        print(f"[DEBUG] Turned right by {request.angle} degrees.")
        return mars_rover_pb2.CommandResponse(success=True, message="Turned right.")

    def TurnOnSpot(self, request, context):
        self.command = "TurnOnSpot"
        self.rover_angle += request.angle
        self.rover_angle %= 360
        print(f"[DEBUG] Turned on spot by {request.angle} degrees.")
        return mars_rover_pb2.CommandResponse(success=True, message="Turned on the spot.")

    def StopMovement(self, request, context):
        self.command = "StopMovement"
        print("[DEBUG] Movement stopped.")
        return mars_rover_pb2.CommandResponse(success=True, message="Stopped.")

    def _update_path(self):
        """Add current position to the traced path."""
        self.path.append(self.rover_pos[:])

def game_loop(server, scanned_surface, args):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rover Mapping - gRPC Controlled")
    clock = pygame.time.Clock()

    view_offset = [-WIDTH // 2, -HEIGHT // 2]

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, view_offset)
        draw_path(screen, server.path, view_offset)
        draw_rover(screen, server.rover_pos, view_offset)
        draw_arrows(screen, server.rover_pos, server.rover_angle, server.mast_angle, view_offset)
        draw_fov(screen, server.rover_pos, server.mast_angle, view_offset)

        if server.trace_scanned_area:
            update_scanned_area(scanned_surface, server.rover_pos, server.mast_angle, view_offset)

        # Handle StopMovement explicitly
        if server.command and server.command == "StopMovement":
            server.command = None

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

        # Adjust view offset for smooth scrolling
        if server.rover_pos[0] - view_offset[0] < WIDTH // 4:
            view_offset[0] -= WIDTH // 10
        elif server.rover_pos[0] - view_offset[0] > 3 * WIDTH // 4:
            view_offset[0] += WIDTH // 10
        if server.rover_pos[1] - view_offset[1] < HEIGHT // 4:
            view_offset[1] -= HEIGHT // 10
        elif server.rover_pos[1] - view_offset[1] > 3 * HEIGHT // 4:
            view_offset[1] += HEIGHT // 10

        draw_hud(screen, [], [], len(server.path), 0, server.rover_pos)
        pygame.display.flip()
        clock.tick(30)

def main():
    parser = argparse.ArgumentParser(description="Rover Mapping with gRPC")
    parser.add_argument("--load-last", action="store_true", help="Load the last saved map.")
    parser.add_argument("--new-map", action="store_true", help="Start a new map.")
    parser.add_argument("--server", type=str, default="localhost:50051", help="Address of the gRPC server.")
    args = parser.parse_args()

    server = MappingServer()
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mars_rover_pb2_grpc.add_RoverServiceServicer_to_server(server, grpc_server)
    grpc_server.add_insecure_port(args.server)
    grpc_server.start()

    scanned_surface = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)
    game_loop(server, scanned_surface, args)

if __name__ == "__main__":
    main()