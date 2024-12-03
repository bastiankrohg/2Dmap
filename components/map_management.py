import os
import json
from datetime import datetime
from components.constants import MAPS_DIR

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

def save_map(path, rover_pos, resources, obstacles, name=None):
    """Saves the map to a file."""
    if name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_map.json"
    else:
        filename = name

    filepath = os.path.join(MAPS_DIR, filename)

    map_data = {
        "path": path,
        "rover_pos": rover_pos,
        "resources": resources,
        "obstacles": obstacles,
    }

    with open(filepath, "w") as f:
        json.dump(map_data, f, indent=4)
    print(f"[DEBUG] Map saved to {filepath}")

    # Update the last-used map
    save_last_used_map(filename)


def load_map(filepath):
    """Loads a map from a file."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        # Validate loaded path
        path = [
            tuple(pos) for pos in data.get("path", [])
            if isinstance(pos, list) and len(pos) == 2 and all(isinstance(coord, (int, float)) for coord in pos)
        ]

        rover_pos = data.get("rover_pos", [400, 400])
        resources = data.get("resources", [])
        obstacles = data.get("obstacles", [])

        return path, rover_pos, resources, obstacles
    except FileNotFoundError:
        print(f"[ERROR] Map file '{filepath}' not found.")
        return [], [400, 400], [], []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to decode map file '{filepath}': {e}")
        return [], [400, 400], [], []
    

def list_maps():
    files = [f for f in os.listdir(MAPS_DIR) if f.endswith(".json")]
    for i, file in enumerate(files):
        print(f"{i + 1}: {file}")
    return files

def reset_map():
    """Resets the map to an initial state."""
    return [], [400, 400], [], []