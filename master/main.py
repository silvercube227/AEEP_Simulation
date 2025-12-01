# main.py - this file reads both imu and force simultaneously
#imports are outdated - need to update from new force sensing data
from force_analysis import update_mesh_color
from force_analysis import force_analysis
from force_reader_ import read_flex_data
from master.imu.imu_reader import read_imu_data
from dof9_filter import MadgwickFilter
import pyvista as pv
import numpy as np
import random
import time

def main():
    
    stl_file = r"C:\Users\kayla\.spyder-py3\DT3_Local\bph_mold_combined.stl"
    mesh = pv.read(stl_file)
    min_x, max_x, min_y, max_y, min_z, max_z = mesh.bounds
    translation_vector = np.array([min_x, min_y, min_z])
    mesh.translate(translation_vector)
    
    box_corners = np.array([[min_x, min_y, min_z], [max_x, min_y, min_z], [max_x, max_y, min_z], 
                           [min_x, max_y, min_z], [min_x, min_y, max_z], [max_x, min_y, max_z], 
                           [max_x, max_y, max_z], [min_x, max_y, max_z]])
    
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],  # Bottom edges
        [4, 5], [5, 6], [6, 7], [7, 4],  # Top edges
        [0, 4], [1, 5], [2, 6], [3, 7]   # Vertical edges
    ]
    
    border_lines = pv.PolyData()
    for edge in edges:
        start_point = box_corners[edge[0]]
        end_point = box_corners[edge[1]]
        line = pv.Line(start_point, end_point)
        border_lines += line
    
    # Create a PyVista plotter
    plotter = pv.Plotter()
    mesh_actor = plotter.add_mesh(mesh, color="white", show_edges=True, opacity=0.25)
    
    # Add marker at the center initially
    marker_position = mesh.center
    marker = pv.PolyData(np.array([marker_position]))
    plotter.add_mesh(marker, color="cyan", render_points_as_spheres=True, point_size=20)
    
    # Set window size
    plotter.window_size = [1200, 900]
    
    # Add the border edges
    plotter.add_mesh(border_lines, color="blue", line_width=2)
    
    # Show axes indicator
    plotter.show_axes()
    
    
    
    # force_text = plotter.add_text("Force: 0.0 N", position="upper_left", font_size=12)

    # Define the threshold force that triggers the red glow (5N)
    # force_threshold1 = 5.0
    # force_threshold2 = 10.0
    
    def update_position(current_position):
        marker.points = np.array([current_position])        
        mesh_actor.Modified()
        plotter.update()

    df = []
    time_above_pressure_thresh = 0
    time_threshold = 3.0
    force_threshold = 10.0
  
    x_min = -75.485
    x_max = 75.485
    y_min = -82.4505
    y_max = 82.4505
    z_min = -63.0095
    z_max = 63.0095
  
    x = 0
    y = 0
    z = 0 

    start_time = time.time()
    plotter.iren.add_observer('TimerEvent', update_position)
    plotter.iren.create_timer(300)
    plotter.show(auto_close=False, interactive_update=True)

    while (
      x_min <= x <= x_max and
      y_min <= y <= y_max and
      z_min <= z <= z_max
    ):
        print("meowmeowmeowmeow")
        current_time = time.time()
        dt = current_time - start_time
        start_time = current_time

        ax, ay, az, gx, gy, gz, mx, my, mz = read_imu_data()
        #N, S, E, W = read_flex_data()

        madgwick = MadgwickFilter(sample_period=dt, beta=0.1)
        position = madgwick.compute_position([dt, ax, ay, az, gx, gy, gz, mx, my, mz], beta=0.1, L=0.1)
        
        # pressure = force_analysis(bend_values)

        
      
        update_position(position) # update point on minimap
        
        
        # 300 milliseconds for better visualization
        # Show the plotter window
        

        # force thresholding

        # if pressure > force_threshold:
        #     time_above_pressure_thresh += dt
        # else:
        #     time_above_pressure_thresh = 0

        # if time_above_pressure_thresh > time_threshold:
        #     update_mesh_color(pressure, mesh_actor, plotter, force_threshold1, force_threshold2)

        # Set up the timer
    

    N, S, E, W = read_flex_data()
    data = {dt, position, N, S, E, W}
    df.append(data)

if __name__ == "__main__":
    main()
