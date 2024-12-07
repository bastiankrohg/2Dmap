import argparse
import grpc
import pygame
import math
from concurrent import futures
from rover_protos import mars_rover_pb2, mars_rover_pb2_grpc
from components.map_management import save_map, load_map, get_last_used_map
from components.drawing import draw_grid, draw_path, draw_rover, draw_arrows, draw_resources, draw_obstacles, draw_fov, update_scanned_area
from components.game_logic import draw_hud, draw_overlay
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR, MAP_SIZE, SCANNED_OFFSET

class MappingServer(mars_rover_pb2_grpc.RoverServiceServicer):
    def __init__(self):
        self.command = None
        self.rover_pos = [0, 0]  # Start at (0, 0)
        self.rover_angle = 0
        self.mast_angle = 0
        self.path = []
        self.resources = []
        self.obstacles = []
        self.trace_scanned_area = False
        self.show_resource_list = False
        self.show_obstacle_list = False
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
        self.rover_angle += request.angle
        self.rover_angle %= 360
        return mars_rover_pb2.CommandResponse(success=True, message="Turned left.")

    def TurnRight(self, request, context):
        self.command = "TurnRight"
        self.rover_angle -= request.angle
        self.rover_angle %= 360
        return mars_rover_pb2.CommandResponse(success=True, message="Turned right.")

    def TurnOnSpot(self, request, context):
        self.command = "TurnOnSpot"
        self.rover_angle += request.angle
        self.rover_angle %= 360
        return mars_rover_pb2.CommandResponse(success=True, message="Turned on the spot.")

    def StopMovement(self, request, context):
        self.command = "StopMovement"
        return mars_rover_pb2.CommandResponse(success=True, message="Stopped movement.")

    def MapResource(self, request, context):
        resource_position = self._compute_position(request.distance)
        resource_data = {
            "position": resource_position,
            "size": request.size if request.size else 5,  # Default size
            "object": request.object if request.object else "N/A",  # Default object label
        }
        self.resources.append(resource_data)
        return mars_rover_pb2.CommandResponse(success=True, message=f"Resource mapped: {resource_data['object']}")

    def MapObstacle(self, request, context):
        obstacle_position = self._compute_position(request.distance)
        obstacle_data = {
            "position": obstacle_position,
            "size": request.size if request.size else 3,  # Default size
            "object": request.object if request.object else "N/A",  # Default object label
        }
        self.obstacles.append(obstacle_data)
        return mars_rover_pb2.CommandResponse(success=True, message=f"Obstacle mapped: {obstacle_data['object']}")

    def ToggleResourceList(self, request, context):
        self.show_resource_list = not self.show_resource_list
        return mars_rover_pb2.CommandResponse(success=True, message="Toggled resource list display.")

    def ToggleObstacleList(self, request, context):
        self.show_obstacle_list = not self.show_obstacle_list
        return mars_rover_pb2.CommandResponse(success=True, message="Toggled obstacle list display.")

    def _compute_position(self, distance):
        """Calculate position based on current rover position and mast angle."""
        rad_angle = math.radians(self.mast_angle)
        dx = distance * math.cos(rad_angle)
        dy = -distance * math.sin(rad_angle)
        return [self.rover_pos[0] + dx, self.rover_pos[1] + dy]

    def _update_path(self):
        """Add the current position to the traced path."""
        self.path.append(self.rover_pos[:])

def game_loop(server, scanned_surface, args):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rover Mapping - gRPC Controlled")
    clock = pygame.time.Clock()

    view_offset = [0, 0]  # Centered on the starting position
    
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, view_offset)
        draw_path(screen, server.path, view_offset)
        draw_rover(screen, server.rover_pos, view_offset)
        draw_arrows(screen, server.rover_pos, server.rover_angle, server.mast_angle, view_offset)
        draw_fov(screen, server.rover_pos, server.mast_angle, view_offset)

        draw_resources(screen, server.resources, view_offset)
        draw_obstacles(screen, server.obstacles, view_offset)

        if server.trace_scanned_area:
            update_scanned_area(scanned_surface, server.rover_pos, server.mast_angle, [-WIDTH // 2, -HEIGHT // 2])

        # Blit the scanned surface
        screen.blit(
            scanned_surface,
            (0, 0),
            pygame.Rect(SCANNED_OFFSET[0], SCANNED_OFFSET[1], WIDTH, HEIGHT),
        )

        # Show resource or obstacle lists if toggled
        if server.show_resource_list:
            draw_overlay(screen, "Resources", server.resources)
        if server.show_obstacle_list:
            draw_overlay(screen, "Obstacles", server.obstacles)

        # Adjust view offset for smooth scrolling
        if server.rover_pos[0] - view_offset[0] < WIDTH // 4:
            view_offset[0] -= WIDTH // 10
        elif server.rover_pos[0] - view_offset[0] > 3 * WIDTH // 4:
            view_offset[0] += WIDTH // 10
        if server.rover_pos[1] - view_offset[1] < HEIGHT // 4:
            view_offset[1] -= HEIGHT // 10
        elif server.rover_pos[1] - view_offset[1] > 3 * HEIGHT // 4:
            view_offset[1] += HEIGHT // 10

        # Draw HUD
        draw_hud(screen, server.resources, server.obstacles, len(server.path), 0, server.rover_pos)

        pygame.display.flip()
        clock.tick(30)

def main():
    parser = argparse.ArgumentParser(description="Rover Mapping with gRPC")
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