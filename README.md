 # Mars Rover Mapping Module

This repository contains the modules and scripts for mapping and controlling a Mars Rover simulation. The functionality includes a standard map testing module, gRPC communication for remote rover control, and additional simulation features for sensors and mapping.

---

## Setup and Environment

### Prerequisites
- Python 3.9 or later
- Required Python packages:
  - `pygame`
  - `grpcio`
  - `grpcio-tools`

Install the dependencies using the following command:

```bash
pip install pygame grpcio grpcio-tools
```

---

### Normal Testing with the Map Module

To run the map testing module without gRPC, use the `game_map.py` script. This mode provides a standalone environment to simulate mapping functionality.

#### Steps to Run:
1. Navigate to the directory containing the `game_map.py` file.
2. Run the script:

```bash
python game_map.py
```

---

### gRPC Testing with the Map Module

To test the map module with gRPC, you'll need to start multiple components: 
1. The `game_map_grpc.py` script for the Pygame map viewer.
2. The `control.py` script for controlling the rover.
3. The `dummy_ultrasound.py` script to simulate the ultrasound sensor readings.

#### Steps to Run:
1. Start the **dummy ultrasound sensor**:
   - Navigate to the `rover-pi` directory.
   - Run the script:
   ```bash
   python dummy_ultrasound.py
   ```
2. Start the control interface:
   - Navigate to the rover-coral directory.
   - Run the script:
   ```bash
   python control.py
   ```
3.	Start the Pygame map viewer:
   - Navigate to the directory containing the game_map_grpc.py file.
   - Run the script:
   ```bash
   python game_map_grpc.py
   ```

Once all components are running, you should be able to interact with the rover/mapping module using the controls listed in the next section.

---

### Controls and Functionality (gRPC Version)

When running the `game_map_grpc.py` script, you can control the rover and interact with the map using the following keys:

#### Rover Movement
- **W**: Move forward.
- **S**: Move backward.
- **A**: Turn left while moving.
- **D**: Turn right while moving.
- **Q**: Rotate mast left (periscope direction).
- **E**: Rotate mast right.
- **R**: Stop all movement.

#### LED Controls
- **H**: Toggle headlights.
- **1-6**: Toggle individual wheel status LEDs.

#### Mapping
- **M**: Map a resource at the current mast position.
- **N**: Map an obstacle at the current mast position.
- **Tab**: Toggle the resource list.
- **Shift**: Toggle the obstacle list.

#### Scanning
- **T**: Toggle scanning mode (activates the mast's scanning field of view).

#### Map Navigation
- **Arrow Keys**: Pan the viewport around the map.
- **+/-**: Zoom in/out of the map.

#### Debugging
- **P**: Save the current map to a file (`maps/latest.json`).

Use these controls to test the full functionality of the gRPC-enabled rover mapping module.

---

### Future Updates

#### Updating Message Types
If you need to modify the protocol buffer message definitions, follow these steps:

1. **Update the Protos**
   - Edit the `.proto` files located in the `rover_protos` directory to include the necessary changes.

2. **Compile the Protos**
   - Compile the updated `.proto` files using the following command:
     ```bash
     python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. mars_rover.proto
     ```
   - This will regenerate the `mars_rover_pb2.py` and `mars_rover_pb2_grpc.py` files.

3. **Fix Import Statements**
   - Open the newly generated `mars_rover_pb2_grpc.py` file.
   - Update the import statement for `mars_rover_pb2` by adding a `from .` prefix:
     ```python
     from . import mars_rover_pb2 as mars__rover__pb2
     ```

4. **Update Git Submodules**
   - If the `rover_protos` is a git submodule, ensure it stays updated recursively:
     ```bash
     git submodule update --remote --recursive
     ```

By following these steps, you will ensure that the gRPC message types and associated code are consistent across the project.

## Next Steps

1. **Interface with the Physical Rover Control**
   - Develop and integrate the interface with the physical rover's control system, enabling real-world testing of the mapping module in parallel with the simulation.

2. **Calibrate Rover Movements**
   - Adjust parameters such as turn radius and speed to ensure that the mapping module's traced path aligns closely with the rover's actual movements.
   - Potential future improvement: Implement an odometer based on wheel motor feedback to report actual distance traveled, improving accuracy over the current estimated values.

3. **Pathfinding Algorithms**
   - Add a pathfinding algorithm that considers a constrained range variable and calculates the fastest route to visit all resources.
   - Implement an algorithm to maximize area search coverage, potentially integrating with a pattern generator for search-and-rescue (SAR) patterns. This could function like an autopilot, generating a sequence of commands for the rover to execute.

4. **Autonomous Decision-Making**
   - Implement decision-making logic for obstacle avoidance and resource prioritization during exploration.

Optional, if we have time:

5. **Real-Time Map Synchronization**
   - Enable real-time synchronization of the rover's map with a web interface or cloud service, allowing for monitoring and decision-making during operations.

6. **Testing in Varied Environments**
   - Conduct testing in different terrains and environments, such as rocky surfaces, sandy areas, or dense vegetation, to validate the module's robustness.

7. **Energy Management Algorithms**
    - Incorporate algorithms to optimize rover movement and sensor usage based on available power resources.

8. **Simulation Enhancements**
    - Expand the simulation module to include environmental variables such as wind, terrain friction, or rover hardware degradation.
