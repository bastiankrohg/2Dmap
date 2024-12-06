import argparse
import grpc
from concurrent import futures
import pygame
from rover_protos import mars_rover_pb2, mars_rover_pb2_grpc
from components.map_management import save_map, load_map, get_last_used_map
from components.drawing import draw_grid, draw_path, draw_rover, draw_fov, update_scanned_area
from components.game_logic import update_rover_position, draw_hud
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR, MAP_SIZE

class MappingServer(mars_rover_pb2_grpc.RoverServiceServicer):
    def __init__(self, scanned_surface, rover_pos, rover_angle, mast_angle, path, odometer, view_offset, headless=False):
        self.scanned_surface = scanned_surface
        self.rover_pos = rover_pos
        self.rover_angle = rover_angle
        self.mast_angle = mast_angle
        self.path = path
        self.odometer = odometer
        self.view_offset = view_offset
        self.headless = headless
        self.running = True

        # Initialize Pygame if not headless
        if not self.headless:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Rover Mapping - gRPC Server")
            self.clock = pygame.time.Clock()

    # === Command Handlers ===
    def DriveForward(self, request, context):
        speed = request.speed
        print(f"[DEBUG] DriveForward received with speed={speed}")
        self.rover_pos[0] += speed
        self.update_map()
        return mars_rover_pb2.CommandResponse(success=True, message=f"Moved forward by {speed}")

    def Reverse(self, request, context):
        speed = request.speed
        print(f"[DEBUG] Reverse received with speed={speed}")
        self.rover_pos[0] -= speed
        self.update_map()
        return mars_rover_pb2.CommandResponse(success=True, message=f"Moved backward by {speed}")

    def TurnLeft(self, request, context):
        angle = request.angle
        print(f"[DEBUG] TurnLeft received with angle={angle}")
        self.rover_angle -= angle
        self.update_map()
        return mars_rover_pb2.CommandResponse(success=True, message=f"Turned left by {angle} degrees")

    def TurnRight(self, request, context):
        angle = request.angle
        print(f"[DEBUG] TurnRight received with angle={angle}")
        self.rover_angle += angle
        self.update_map()
        return mars_rover_pb2.CommandResponse(success=True, message=f"Turned right by {angle} degrees")

    def StopMovement(self, request, context):
        print("[DEBUG] StopMovement received")
        return mars_rover_pb2.CommandResponse(success=True, message="Stopped movement")

    def RotatePeriscope(self, request, context):
        angle = request.angle
        print(f"[DEBUG] RotatePeriscope received with angle={angle}")
        self.mast_angle += angle
        self.update_map()
        return mars_rover_pb2.CommandResponse(success=True, message=f"Periscope rotated by {angle} degrees")

    # === Map Updating ===
    def update_map(self):
        if not self.headless:
            self.screen.fill(BACKGROUND_COLOR)
            draw_grid(self.screen, self.view_offset)
            draw_path(self.screen, self.path, self.view_offset)
            draw_rover(self.screen, self.rover_pos, self.view_offset)
            draw_fov(self.screen, self.rover_pos, self.mast_angle, self.view_offset)

            # Blit the scanned area
            self.screen.blit(
                self.scanned_surface,
                (0, 0),
                pygame.Rect(
                    self.view_offset[0], self.view_offset[1], WIDTH, HEIGHT
                ),
            )

            draw_hud(self.screen, [], [], self.odometer, 0, self.rover_pos)
            pygame.display.flip()
            self.clock.tick(30)

    def shutdown(self):
        print("[DEBUG] Shutting down the server...")
        self.running = False
        if not self.headless:
            pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="Rover Mapping gRPC Server")
    parser.add_argument("--server", type=str, default="[::]:50051", help="Address for the gRPC server")
    parser.add_argument("--load-last", action="store_true", help="Load the last saved map")
    parser.add_argument("--new-map", action="store_true", help="Start with a new map")
    parser.add_argument("--headless", action="store_true", help="Run without GUI")
    args = parser.parse_args()

    # Load or initialize map
    if args.load_last:
        map_name = get_last_used_map()
        if map_name:
            loaded_data = load_map(map_name)
            if loaded_data:
                path = loaded_data["path"]
                rover_pos = loaded_data["rover_pos"]
                rover_angle = loaded_data["rover_angle"]
                mast_angle = loaded_data["mast_angle"]
                scanned_surface = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)
            else:
                print("[ERROR] Failed to load the last map.")
                return
        else:
            print("[ERROR] No last map available to load.")
            return
    elif args.new_map:
        map_name = "new_map.json"
        path, rover_pos, rover_angle, mast_angle = [], [0, 0], 0, 0
        scanned_surface = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)
    else:
        print("[ERROR] Please specify either --load-last or --new-map.")
        return

    view_offset = [-WIDTH // 2, -HEIGHT // 2]
    odometer = 0

    # Start gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mapping_server = MappingServer(
        scanned_surface, rover_pos, rover_angle, mast_angle, path, odometer, view_offset, headless=args.headless
    )
    mars_rover_pb2_grpc.add_RoverServiceServicer_to_server(mapping_server, server)
    server.add_insecure_port(args.server)
    print(f"[DEBUG] Server running on {args.server}")
    server.start()

    try:
        while mapping_server.running:
            pass
    except KeyboardInterrupt:
        print("[DEBUG] KeyboardInterrupt received.")
        mapping_server.shutdown()
        server.stop(0)


if __name__ == "__main__":
    main()