import os
import json
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

def save_map(path, rover_pos, resources, obstacles, rover_angle, mast_angle, name=None):
    """
    Save map data to a file.

    :param path: The path taken by the rover.
    :param rover_pos: The current position of the rover.
    :param resources: List of resource positions.
    :param obstacles: List of obstacle line segments.
    :param rover_angle: The current heading of the rover.
    :param mast_angle: The current mast direction.
    :param name: The name of the map file.
    """
    map_data = {
        "path": path,
        "rover_pos": rover_pos,
        "resources": resources,
        "obstacles": obstacles,
        "rover_angle": rover_angle,
        "mast_angle": mast_angle,
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
    Load map data from a file.

    :param map_name: The name of the map to load.
    :return: A dictionary containing map data (path, rover_pos, resources, obstacles, rover_angle, mast_angle).
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

        # Debugging output
        print(f"[DEBUG] Map loaded successfully: {map_name}")
        print(f"[DEBUG] rover_pos, rover_angle, mast_angle, resources, obstacles: "
              f"({data['rover_pos']}, {data['rover_angle']}, {data['mast_angle']}, "
              f"{data['resources']}, {data['obstacles']})")

        return data

    except json.JSONDecodeError as e:
        print(f"[ERROR] Map file '{map_name}' is not formatted correctly. Error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error while loading map '{map_name}': {e}")
        return None

def list_maps():
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