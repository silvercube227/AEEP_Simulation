# force_analysis.py

import numpy as np
import math

def force_analysis(n, s, e, w):
    x = e - w
    y = n - s

    angle = math.degrees(math.atan2(x, y))

    if angle < 0:
        angle += 360

    return angle

def update_mesh_color(force, mesh_actor, plotter, force_threshold1, force_threshold2):
    # Update force display text
    plotter.textActor.SetText(0, f"Force: {force:.2f} N")

    if force > force_threshold2:
        intensity = min(1.0, force / 20.0)
        red_value = min(255, 150 + int(105 * intensity))
        color = (red_value/255, 0, 0)

        mesh_actor.GetProperty().SetColor(color)
        mesh_actor.GetProperty().SetOpacity(0.5 + 0.3*intensity)
        mesh_actor.GetProperty().SetAmbient(0.5 + 0.5*intensity)

    elif force > force_threshold1:
        intensity = min(1.0, force / 20.0)
        yellow_value = min(255, 150 + int(105 * intensity))
        color = (yellow_value/255, yellow_value/255, 0)

        mesh_actor.GetProperty().SetColor(color)
        mesh_actor.GetProperty().SetOpacity(0.5 + 0.3*intensity)
        mesh_actor.GetProperty().SetAmbient(0.5 + 0.5*intensity)

    else:
        mesh_actor.GetProperty().SetColor((1, 1, 1))
        mesh_actor.GetProperty().SetOpacity(0.5)
        mesh_actor.GetProperty().SetAmbient(0.0)

    mesh_actor.Modified()
    plotter.render()
