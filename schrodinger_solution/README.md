
# 2D Schrödinger Equation Solver with Taichi and Visualization

This project implements a 2D wave equation solver inspired by the Schrödinger equation using the [Taichi](https://taichi.graphics/) programming language. It simulates the evolution of a wave plane over time, incorporating elements such as boundary conditions, doping effects, and applied voltage. The wave dynamics are visualized in a 2D plane with user-interactive rotation of the 3D wave.

## Features

- **Wave Simulation**: Solves a discretized 2D Schrödinger-like equation to simulate the wave propagation.
- **Doping Effects**: Random variations are applied to the wave plane to simulate physical doping.
- **Voltage Application**: Allows the user to apply voltage across specific regions of the grid, influencing the wave propagation.
- **Interactive Visualization**: The simulation is visualized in 2D with the ability to rotate the view interactively.
- **Color-Coded Wave Visualization**: The height (z-axis) of the wave is color-coded for easy visualization:
  - Green for waves near zero height.
  - Red for waves below a threshold.
  - Blue for waves above a threshold.

## Requirements

- Python 3.x
- [Taichi](https://github.com/taichi-dev/taichi) (`pip install taichi`)
- NumPy (`pip install numpy`)

## How to Run

1. Install the required dependencies using `pip`:
   ```bash
   pip install taichi numpy
   ```

2. Run the Python script:
   ```bash
   python solve_schrodinger.py
   ```

3. The simulation window will open, displaying the 2D plane and the wave propagation.

### Controls

- **Left Mouse Button**: Click and drag to rotate the wave plane visualization in 3D space.
- **GUI Checkbox**: The `Apply Voltage` checkbox in the GUI allows applying voltage to the edges of the wave plane, altering the wave behavior.
  
## Simulation Details

- The wave plane is discretized into a grid with points representing the wave height.
- The simulation evolves based on the following operations:
  - **Laplacian Calculation**: A second-order finite difference method is used to compute the Laplacian of the wave at each grid point.
  - **Wave Update**: The wave height is updated using the computed Laplacian, velocity, and damping factor.
  - **Damping**: A damping term is applied to simulate energy dissipation over time.
  - **Voltage**: Voltage can be applied to the wave plane, affecting the wave height at certain regions.

## Key Functions

- `init_wave_plane()`: Initializes the wave plane with initial conditions.
- `doping()`: Introduces random variations in the wave plane to simulate doping effects.
- `apply_voltage()`: Applies a voltage field to certain regions of the wave plane.
- `solve_schrodinger()`: Computes the Laplacian and updates the wave plane over time.
- `apply_rotation()`: Applies user-driven 3D rotation for visualization.

## Example Output

The program visualizes the wave equation solution with color-coded wave heights. Interacting with the wave plane by rotating it or applying voltage results in dynamic updates to the wave and its behavior.
