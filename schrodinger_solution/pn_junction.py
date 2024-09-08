import taichi as ti
import numpy as np

# Initialize Taichi
ti.init(ti.gpu)

# Define 3D axes (x, y, z) and their colors
np_axis = np.array([[-1, 0, 0], [1, 0, 0], [0, -1, 0], [0, 1, 0], [0, 0, -1], [0, 0, 1]], dtype=np.float32)
axis_3d = ti.Vector.field(3, ti.f32, shape=6)
axis_3d.from_numpy(np_axis)

axis_2d = ti.Vector.field(2, ti.f32, shape=6)
axis_colors = ti.Vector.field(3, ti.i32, shape=6)

# Assign colors for the axes (RGB format)
np_colors = np.array([[255, 0, 0], [255, 0, 0], [0, 255, 0], [0, 255, 0], [0, 0, 255], [0, 0, 255]], dtype=np.int32)
axis_colors.from_numpy(np_colors)

# Fields to store mouse position and movement delta
prev_cursor = ti.Vector.field(2, ti.f32, shape=())
delta = ti.Vector.field(2, ti.f32, shape=())

# Initialize mouse position and delta to zero
prev_cursor[None] = [0.0, 0.0]
delta[None] = [0.0, 0.0]

N = 131072
N_x, N_y = int(ti.sqrt(N)), int(ti.sqrt(N))

# Define wave_plane, points and visualization-related fields
wave_plane = ti.Vector.field(3, ti.f32, shape=(N_x, N_y))
v = ti.field(ti.f32, shape=(N_x, N_y))
points_2d = ti.Vector.field(2, ti.f32, shape=N)   # Used for 2D projection after rotation
points_colors = ti.Vector.field(3, ti.f32, shape=N)

c = 1
dx = 1 / N   
dt = 1e-6
damping = 100000
t=ti.field(ti.f32,shape=())
t[None]=0
@ti.kernel
def init_wave_plane():
    for i, j in wave_plane:
        x = i / N_x * 2.0 - 1.0  # Map x to range [-1, 1]
        y = j / N_y * 2.0 - 1.0  # Map y to range [-1, 1]
        #z = -0.3 if 0.7<=x<= 1 else 0.3
        wave_plane[i, j] = ti.Vector([x, y, 0])  # Store (x, y, z) in wave plane
        v[i, j] = 0
@ti.kernel
def doping():
    for i, j in wave_plane:
        x = i / N_x * 2.0 - 1.0  # Map x to range [-1, 1]
        y = j / N_y * 2.0 - 1.0  # Map y to range [-1, 1]
        if i<=(N_x*0.5) and ti.random()<0.001:
            wave_plane[i,j]=ti.Vector([x,y,-0.5])
        if i>(N_x*0.5) and ti.random()>0.99:
            wave_plane[i,j]=ti.Vector([x,y,0.5])
@ti.kernel
def apply_voltage():
    for i, j in wave_plane:
        x = i / N_x * 2.0 - 1.0  # Map x to range [-1, 1]
        y = j / N_y * 2.0 - 1.0  # Map y to range [-1, 1]
        if i<(N_x*0.2):
            wave_plane[i,j]=ti.Vector([x,y,0.5])
        elif i>N_x*0.8:
            wave_plane[i,j]=ti.Vector([x,y,-1])

@ti.kernel
def solve_schrodinger():
    for i, j in wave_plane:
        if 0 < i < N_x - 1 and 0 < j < N_y - 1:  # Ignore boundary points
            laplacian = (wave_plane[i + 1, j][2] + wave_plane[i - 1, j][2]
                         + wave_plane[i, j + 1][2] + wave_plane[i, j - 1][2]
                         - 4 * wave_plane[i, j][2]) / dx**2
            v[i, j] += c**2 * laplacian * dt
            v[i, j] *= ti.exp(-damping * dt)
            wave_plane[i, j][2] += v[i, j] * dt  # Only update the z-component (wave height)
    t[None]+=dt
axis_original_3d = ti.Vector.field(3, ti.f32, shape=6)

@ti.kernel
def init_axes():
    for i in range(6):
        axis_original_3d[i] = axis_3d[i]

# Kernel for applying the cumulative rotation (for visualization purposes only)
@ti.kernel
def apply_rotation():
    angle_x = cumulative_rotation[None][1]
    angle_y = cumulative_rotation[None][0]

    R_x = ti.Matrix([[1, 0, 0],
                     [0, ti.cos(angle_x), -ti.sin(angle_x)],
                     [0, ti.sin(angle_x), ti.cos(angle_x)]])
    
    R_y = ti.Matrix([[ti.cos(angle_y), 0, ti.sin(angle_y)],
                     [0, 1, 0],
                     [-ti.sin(angle_y), 0, ti.cos(angle_y)]])

    for i in range(6):
        axis_3d[i] = R_y @ (R_x @ axis_original_3d[i])
        axis_2d[i] = 0.5 + 0.3 * ti.Vector([axis_3d[i][0], axis_3d[i][1]])

    # Rotate and project points to 2D
    for i in range(N_x):
        for j in range(N_y):
            idx = i * N_y + j
            point = wave_plane[i, j]  # Use original wave_plane data
            rotated_point = R_y @ (R_x @ point)  # Apply rotation
            points_2d[idx] = 0.5 + 0.5 * ti.Vector([rotated_point[0], rotated_point[1]])  # Projected to 2D
            if 0.1>= wave_plane[i, j][2] >= -0.1:
                points_colors[idx] = ti.Vector([0, 255, 0])  # Color red if z > 0
            elif wave_plane[i, j][2] <-0.1:
                points_colors[idx] = ti.Vector([255, 0, 0]) 
            else:
                points_colors[idx] = ti.Vector([0, 0, 255])  # Color blue if z <= 0

# Initialize the wave plane and axis positions
init_wave_plane()
init_axes()

# Create window
window = ti.ui.Window('2D Screen', res=(1000, 1000))
canvas = window.get_canvas()
gui=window.get_gui()
# Cumulative rotation field for visualization
cumulative_rotation = ti.Vector.field(2, ti.f32, shape=())
cumulative_rotation[None] = [0.0, 0.0]
apply=0
# Main loop
while window.running:

    doping()
    apply=gui.checkbox("apply voltage",apply)
    if apply:
        apply_voltage()

        
    current_mouse_x, current_mouse_y = window.get_cursor_pos()
    if window.is_pressed(ti.ui.LMB):
        delta_x = current_mouse_x - prev_cursor[None][0]
        delta_y = current_mouse_y - prev_cursor[None][1]
        prev_cursor[None] = [current_mouse_x, current_mouse_y]
        cumulative_rotation[None] += [delta_x, delta_y]
    else:
        prev_cursor[None] = [current_mouse_x, current_mouse_y]
    solve_schrodinger()
    apply_rotation()

    canvas.lines(axis_2d, 2e-3, per_vertex_color=axis_colors)
    canvas.circles(points_2d, 9e-4, per_vertex_color=points_colors)
    window.show()