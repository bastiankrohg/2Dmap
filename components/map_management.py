import os
import json
import base64
import numpy as np
import pygame
from datetime import datetime
from components.constants import MAPS_DIR, WIDTH, HEIGHT

LAST_USED_MAP_FILE = os.path.join(MAPS_DIR, "last_used_map.json")

def save_last_used_map(map_name):
    """Saves the name of the last-used map."""
    with open(LAST_USED_MAP_FILE, "w") as f:
        json.dump({"last_used": map_name}, f)
    print(f"[DEBUG] Last-used map updated to {map_name}")


def get_last_used_map():
    """Gets the last-used map name, if available."""
    if os.path.exists(LAST_USED_MAP_FILE):
        with open(LAST_USED_MAP_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_used")
    return None

def save_map(path, rover_pos, resources, obstacles, rover_angle, mast_angle, name=None, scanned_surface=None):
    """
    Save map data to a file, including the scanned zone.

    :param path: The path taken by the rover.
    :param rover_pos: The current position of the rover.
    :param resources: List of resource positions.
    :param obstacles: List of obstacle line segments.
    :param rover_angle: The current heading of the rover.
    :param mast_angle: The current mast direction.
    :param name: The name of the map file.
    :param scanned_surface: The scanned area surface.
    """
    map_data = {
        "path": path,
        "rover_pos": rover_pos,
        "resources": resources,
        "obstacles": obstacles,
        "rover_angle": rover_angle,
        "mast_angle": mast_angle,
    }

    # Add scanned surface data if provided
    if scanned_surface:
        scanned_array = pygame.surfarray.array_alpha(scanned_surface)
        scanned_data = base64.b64encode(scanned_array.tobytes()).decode('utf-8')
        map_data["scanned_zone"] = {
            "data": scanned_data,
            "size": scanned_surface.get_size(),
        }

    file_name = f"maps/{name or 'map.json'}"
    try:
        with open(file_name, "w") as file:
            json.dump(map_data, file, indent=4)
        print(f"[DEBUG] Map saved to {file_name}")
    except Exception as e:
        print(f"[ERROR] Failed to save map: {e}")

def load_map(map_name):
    """
    Load map data from a file, including the scanned zone.

    :param map_name: The name of the map to load.
    :return: A dictionary containing map data (path, rover_pos, resources, obstacles, rover_angle, mast_angle, scanned_surface).
    """
    file_path = os.path.join("maps", map_name)
    if not os.path.exists(file_path):
        print(f"[ERROR] Map file '{map_name}' not found.")
        return None

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        # Ensure all required keys are present
        required_keys = ["path", "rover_pos", "resources", "obstacles", "rover_angle", "mast_angle"]
        for key in required_keys:
            if key not in data:
                print(f"[ERROR] Map file '{map_name}' is missing key: '{key}'.")
                return None

        # Recreate the scanned surface if present
        scanned_surface = None
        if "scanned_zone" in data:
            scanned_zone = data["scanned_zone"]
            scanned_size = tuple(scanned_zone["size"])
            scanned_data = base64.b64decode(scanned_zone["data"])
            scanned_array = np.frombuffer(scanned_data, dtype=np.uint8).reshape(scanned_size[1], scanned_size[0])
            scanned_surface = pygame.Surface(scanned_size, pygame.SRCALPHA)
            pygame.surfarray.blit_array(scanned_surface, np.dstack((np.zeros_like(scanned_array), scanned_array)))

        # Debugging output
        print(f"[DEBUG] Map loaded successfully: {map_name}")
        print(f"[DEBUG] rover_pos, rover_angle, mast_angle, resources, obstacles: "
              f"({data['rover_pos']}, {data['rover_angle']}, {data['mast_angle']}, "
              f"{data['resources']}, {data['obstacles']})")

        return {
            "path": data["path"],
            "rover_pos": data["rover_pos"],
            "resources": data["resources"],
            "obstacles": data["obstacles"],
            "rover_angle": data["rover_angle"],
            "mast_angle": data["mast_angle"],
            "scanned_surface": scanned_surface
        }

    except json.JSONDecodeError as e:
        print(f"[ERROR] Map file '{map_name}' is not formatted correctly. Error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error while loading map '{map_name}': {e}")
        return None

def list_maps():
    """List all saved maps."""
    files = [f for f in os.listdir(MAPS_DIR) if f.endswith(".json")]
    for i, file in enumerate(files):
        print(f"{i + 1}: {file}")
    return files

def reset_map():
    """Resets the map to a blank state with rover centered."""
    path = []  # Clear the path
    rover_pos = [WIDTH // 2, HEIGHT // 2]  # Start in the center
    resources = []  # Clear resources
    obstacles = []  # Clear obstacles
    return path, rover_pos, resources, obstacles