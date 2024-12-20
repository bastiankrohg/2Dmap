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
        self.scanned_surface = None
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
        self.mast_angle = (self.mast_angle + request.angle) % 360
        return mars_rover_pb2.CommandResponse(success=True, message="Turned left.")

    def TurnRight(self, request, context):
        self.command = "TurnRight"
        self.rover_angle -= request.angle
        self.rover_angle %= 360
        self.mast_angle = (self.mast_angle - request.angle) % 360
        return mars_rover_pb2.CommandResponse(success=True, message="Turned right.")

    def TurnOnSpot(self, request, context):
        self.command = "TurnOnSpot"
        self.rover_angle += request.angle
        self.rover_angle %= 360
        self.mast_angle = (self.mast_angle + request.angle) % 360
        return mars_rover_pb2.CommandResponse(success=True, message="Turned on the spot.")

    def RotatePeriscope(self, request, context):
        """Rotate the mast by the given angle."""
        self.mast_angle = (self.mast_angle + request.angle) % 360
        print(f"[DEBUG] Mast rotated to {self.mast_angle} degrees.")
        return mars_rover_pb2.CommandResponse(success=True, message="Mast rotated.")

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

    def ToggleScan(self, request, context):
        """
        Toggle the scanning mode.
        """
        self.trace_scanned_area = not self.trace_scanned_area
        status = "enabled" if self.trace_scanned_area else "disabled"
        print(f"[DEBUG] Scanning {status}.")
        return mars_rover_pb2.CommandResponse(success=True, message=f"Scanning {status}.")

    def SaveMap(self, request, context):
        save_map(
            self.path,
            self.rover_pos,
            self.resources,
            self.obstacles,
            self.rover_angle,
            self.mast_angle,
            name=request.file_name if request.file_name else "map.json",
        )
        return mars_rover_pb2.CommandResponse(success=True, message="Map saved successfully.")

    def _compute_position(self, distance):
        corrected_angle = (self.mast_angle + 90) % 360  # Correct the offset
        rad_angle = math.radians(corrected_angle)
        dx = distance * math.cos(rad_angle)
        dy = -distance * math.sin(rad_angle)  # Invert for Pygame's y-axis
        return [self.rover_pos[0] + dx, self.rover_pos[1] + dy]

    def _update_path(self):
        """Add the current position to the traced path."""
        self.path.append(self.rover_pos[:])

def game_loop(server, args):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rover Mapping - gRPC Controlled")
    clock = pygame.time.Clock()

    view_offset = [-WIDTH // 2, - HEIGHT // 2]  # Centered on the starting position
    
    while True:
        screen.fill(BACKGROUND_COLOR)

        draw_grid(screen, view_offset)
        draw_path(screen, server.path, view_offset)
        draw_rover(screen, server.rover_pos, view_offset)
        draw_arrows(screen, server.rover_pos, server.rover_angle, server.mast_angle, view_offset)

        draw_resources(screen, server.resources, view_offset)
        draw_obstacles(screen, server.obstacles, view_offset)

        if server.trace_scanned_area:
            draw_fov(screen, server.rover_pos, server.mast_angle, view_offset)
            update_scanned_area(server.scanned_surface, server.rover_pos, server.mast_angle)

        # Blit scanned surface adjusted for viewport
        screen.blit(
            server.scanned_surface,
            (view_offset[0] + SCANNED_OFFSET[0], view_offset[1] + SCANNED_OFFSET[1]),
            pygame.Rect(0, 0, MAP_SIZE, MAP_SIZE)
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

    server.scanned_surface = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)
    server.scanned_surface.fill((0, 0, 0, 0))  # Fully transparent background

    try:
        game_loop(server, args)
    except KeyboardInterrupt:
        print("[DEBUG] Shutting down gRPC server.")
        grpc_server.stop(0)  # Stop the server gracefully
        pygame.quit()
        exit(0)

if __name__ == "__main__":
    main()