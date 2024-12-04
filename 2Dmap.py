import grpc
import pygame
from main.menu import menu_screen
from main.game import game_loop
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR
from rover_protos import mars_rover_pb2, mars_rover_pb2_grpc


class MappingClient:
    """
    gRPC Client for communicating with the rover and controlling the mapping game.
    """

    def __init__(self, server_address):
        print("[DEBUG] Connecting to rover server...")
        self.channel = grpc.insecure_channel(server_address)
        self.stub = mars_rover_pb2_grpc.RoverServiceStub(self.channel)
        print("[DEBUG] Connected to rover server.")

    # === Locomotion Commands ===
    def send_drive_forward(self, speed):
        response = self.stub.DriveForward(mars_rover_pb2.DriveRequest(speed=speed))
        print(f"[DEBUG] DriveForward Response: {response.message}")
        return response

    def send_reverse(self, speed):
        response = self.stub.Reverse(mars_rover_pb2.DriveRequest(speed=speed))
        print(f"[DEBUG] Reverse Response: {response.message}")
        return response

    def send_turn_left(self, angle):
        response = self.stub.TurnLeft(mars_rover_pb2.TurnRequest(angle=angle))
        print(f"[DEBUG] TurnLeft Response: {response.message}")
        return response

    def send_turn_right(self, angle):
        response = self.stub.TurnRight(mars_rover_pb2.TurnRequest(angle=angle))
        print(f"[DEBUG] TurnRight Response: {response.message}")
        return response

    def send_stop(self):
        response = self.stub.StopMovement(mars_rover_pb2.StopRequest())
        print(f"[DEBUG] StopMovement Response: {response.message}")
        return response

    # === Utility Functions ===
    def send_rotate_periscope(self, angle):
        response = self.stub.RotatePeriscope(mars_rover_pb2.RotateRequest(angle=angle))
        print(f"[DEBUG] RotatePeriscope Response: {response.message}")
        return response

    def get_ultrasound_measurement(self):
        response = self.stub.GetUltrasoundMeasurement(mars_rover_pb2.UltrasoundRequest())
        print(f"[DEBUG] UltrasoundMeasurement: {response.distance} cm")
        return response.distance


def main():
    """
    Main entry point for running the gRPC client and mapping game.
    """
    server_address = "localhost:50051"  # Update with your gRPC server address if different
    client = MappingClient(server_address)

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rover Mapping with gRPC")
    screen.fill(BACKGROUND_COLOR)
    pygame.display.flip()

    # Menu and game flow
    map_name = menu_screen()
    if map_name:
        print(f"[DEBUG] Loading map: {map_name}")
        # Start game with existing map
        game_loop(client, map_name=map_name)
    else:
        print("[DEBUG] Starting a new map...")
        # Start game with a new map
        game_loop(client)

    print("[DEBUG] Shutting down...")
    pygame.quit()


if __name__ == "__main__":
    main()