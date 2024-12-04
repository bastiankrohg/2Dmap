import os

# Screen dimensions
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 20

# Create a full-size surface for the scanned area
MAP_SIZE = 10000 # For example

# Center the scanned_surface so it supports negative coordinates
SCANNED_OFFSET = [MAP_SIZE // 2, MAP_SIZE // 2]

# Colors
ROVER_COLOR = (0, 255, 0)
MAST_COLOR = (0, 0, 255)
RESOURCE_COLOR = (0, 255, 255)
OBSTACLE_COLOR = (255, 0, 0)
PATH_COLOR = (200, 200, 200)
BACKGROUND_COLOR = (0, 0, 0)

# Distances
RESOURCE_DISTANCE = 15
OBSTACLE_DISTANCE = 15
OBSTACLE_LENGTH = 30

# FOV Mast
FOV_ANGLE = 90  # Field of view angle in degrees
FOV_DISTANCE = 200  # Maximum distance for the field of view
FOV_COLOR = (255, 255, 0, 100)  # Semi-transparent yellow

# Fonts
HUD_FONT_SIZE = 24
MENU_FONT_SIZE = 36

# Map directory
MAPS_DIR = "maps"
os.makedirs(MAPS_DIR, exist_ok=True)

# Rover
ROVER_SPEED = 5  # Speed of the rover in pixels per frame
