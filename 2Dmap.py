import argparse
import grpc
import pygame
from rover_protos import mars_rover_pb2, mars_rover_pb2_grpc
from components.map_management import save_map, load_map, get_last_used_map
from components.drawing import draw_grid, draw_path, draw_rover, draw_fov, update_scanned_area
from components.game_logic import update_rover_position, draw_hud
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR, MAP_SIZE

class MappingClient:
    def __init__(self, server_address, headless=False):
        print("[DEBUG] Connecting to rover server...")
        self.channel = grpc.insecure_channel(server_address)
        self.stub = mars_rover_pb2_grpc.RoverServiceStub(self.channel)
        self.headless = headless
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


def game_loop(client, scanned_surface, rover_pos, rover_angle, mast_angle, path, odometer, view_offset):
    """Run the mapping logic with or without GUI."""
    if not client.headless:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Rover Mapping - gRPC Controlled")
        clock = pygame.time.Clock()

    running = True
    while running:
        if not client.headless:
            screen.fill(BACKGROUND_COLOR)
            draw_grid(screen, view_offset)
            draw_path(screen, path, view_offset)
            draw_rover(screen, rover_pos, view_offset)
            draw_fov(screen, rover_pos, mast_angle, view_offset)

            # Blit scanned area
            screen.blit(
                scanned_surface,
                (0, 0),
                pygame.Rect(
                    view_offset[0], view_offset[1], WIDTH, HEIGHT
                ),
            )

        # Update rover position based on gRPC commands
        keys = pygame.key.get_pressed() if not client.headless else None
        rover_pos, rover_angle, path, odometer, mast_angle = update_rover_position(
            keys, rover_pos, rover_angle, path, odometer, mast_angle
        )

        if not client.headless:
            draw_hud(screen, [], [], odometer, 0, rover_pos)  # Simplified HUD
            pygame.display.flip()
            clock.tick(30)

        # Exit gracefully in headless mode
        if client.headless:
            break

    if not client.headless:
        pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="Rover Mapping Game with gRPC")
    parser.add_argument("--server", type=str, default="localhost:50051", help="Address of the gRPC server")
    parser.add_argument("--load-last", action="store_true", help="Load the last saved map")
    parser.add_argument("--new-map", action="store_true", help="Start with a new map")
    parser.add_argument("--headless", action="store_true", help="Run without GUI")
    args = parser.parse_args()

    # Initialize client
    client = MappingClient(args.server, headless=args.headless)

    # Load map or start new
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

    # Run the game loop
    game_loop(client, scanned_surface, rover_pos, rover_angle, mast_angle, path, odometer, view_offset)


if __name__ == "__main__":
    main()