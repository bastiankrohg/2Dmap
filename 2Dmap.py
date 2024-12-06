import argparse
import grpc
import pygame
from concurrent import futures
from rover_protos import mars_rover_pb2, mars_rover_pb2_grpc
from components.map_management import save_map, load_map, get_last_used_map
from components.drawing import draw_grid, draw_path, draw_rover, draw_fov, update_scanned_area
from components.game_logic import update_rover_position, draw_hud
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR, MAP_SIZE, SCANNED_OFFSET
from components.utils import compute_resource_position, compute_obstacle_positions

class MappingServer(mars_rover_pb2_grpc.RoverServiceServicer):
    def __init__(self):
        self.rover_pos = [WIDTH // 2, HEIGHT // 2]
        self.rover_angle = 0
        self.mast_angle = 0
        self.path = []
        self.trace_scanned_area = False
        self.resources = []
        self.obstacles = []
        print("[DEBUG] MappingServer initialized.")

    def DriveForward(self, request, context):
        self.rover_pos[1] -= request.speed
        self._update_path()
        return mars_rover_pb2.CommandResponse(success=True, message="Moved forward.")

    def Reverse(self, request, context):
        self.rover_pos[1] += request.speed
        self._update_path()
        return mars_rover_pb2.CommandResponse(success=True, message="Reversed.")

    def TurnLeft(self, request, context):
        angle = request.angle
        print(f"[DEBUG] Received TurnLeft command with angle: {angle}")
        self.rover_angle -= angle  # Rotate counter-clockwise
        return mars_rover_pb2.CommandResponse(success=True, message=f"Turning left by {angle} degrees")

    def TurnRight(self, request, context):
        angle = request.angle
        print(f"[DEBUG] Received TurnRight command with angle: {angle}")
        self.rover_angle += angle  # Rotate clockwise
        return mars_rover_pb2.CommandResponse(success=True, message=f"Turning right by {angle} degrees")

    def StopMovement(self, request, context):
        return mars_rover_pb2.CommandResponse(success=True, message="Stopped.")

    def RotatePeriscope(self, request, context):
        angle = request.angle
        print(f"[DEBUG] Received RotatePeriscope command with angle: {angle}")
        self.mast_angle = angle  # Update the mast angle
        return mars_rover_pb2.CommandResponse(success=True, message=f"Mast rotated to {angle} degrees")

    def ControlHeadlights(self, request, context):
        return mars_rover_pb2.CommandResponse(success=True, message="Headlights toggled.")

    def ControlWheelLEDs(self, request, context):
        return mars_rover_pb2.CommandResponse(success=True, message="Wheel LEDs toggled.")

    def PlaceResource(self, request, context):
        print("[DEBUG] Received PlaceResource command")
        distance = request.distance or 0
        resource_pos = compute_resource_position(self.rover_pos, self.mast_angle, distance)
        self.resources.append(resource_pos)
        return mars_rover_pb2.CommandResponse(success=True, message="Resource placed")

    def PlaceObstacle(self, request, context):
        print("[DEBUG] Received PlaceObstacle command")
        distance = request.distance or 0
        obstacle_pos = compute_obstacle_positions(self.rover_pos, self.mast_angle, distance)
        self.obstacles.append(obstacle_pos)
        return mars_rover_pb2.CommandResponse(success=True, message="Obstacle placed")

    def _update_path(self):
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
        draw_fov(screen, server.rover_pos, server.mast_angle, view_offset)

        if server.trace_scanned_area:
            update_scanned_area(scanned_surface, server.rover_pos, server.mast_angle, view_offset)

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

        # Adjust view offset
        if server.rover_pos[0] - view_offset[0] < WIDTH // 4:
            view_offset[0] -= WIDTH // 10
        elif server.rover_pos[0] - view_offset[0] > 3 * WIDTH // 4:
            view_offset[0] += WIDTH // 10
        if server.rover_pos[1] - view_offset[1] < HEIGHT // 4:
            view_offset[1] -= HEIGHT // 10
        elif server.rover_pos[1] - view_offset[1] > 3 * HEIGHT // 4:
            view_offset[1] += HEIGHT // 10

        draw_hud(screen, server.resources, server.obstacles, len(server.path), 0, server.rover_pos)
        pygame.display.flip()
        clock.tick(30)


def main():
    parser = argparse.ArgumentParser(description="Rover Mapping with gRPC")
    parser.add_argument("--load-last", action="store_true", help="Load the last saved map.")
    parser.add_argument("--new-map", action="store_true", help="Start a new map.")
    parser.add_argument("--server", type=str, default="localhost:50051", help="Address of the gRPC server.")
    args = parser.parse_args()

    # Initialize gRPC server
    server = MappingServer()
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mars_rover_pb2_grpc.add_RoverServiceServicer_to_server(server, grpc_server)
    grpc_server.add_insecure_port(args.server)
    grpc_server.start()

    # Setup map
    scanned_surface = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)
    if args.load_last:
        map_name = get_last_used_map()
        if map_name:
            loaded_data = load_map(map_name)
            if loaded_data:
                server.path = loaded_data["path"]
                server.rover_pos = loaded_data["rover_pos"]
                scanned_surface = pygame.image.load(loaded_data["scanned_surface"]).convert_alpha()
    elif args.new_map:
        map_name = "new_map.json"
    else:
        print("[ERROR] Please specify --load-last or --new-map.")
        return

    game_loop(server, scanned_surface, args)


if __name__ == "__main__":
    main()