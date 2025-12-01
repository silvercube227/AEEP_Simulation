def determine_quadrant(n, s, e, w, threshold = 15):
    vertical = n - s
    horizontal = e - w

    if abs(vertical) < threshold:
        vertical = 0
    if abs(horizontal) < threshold:
        horizontal = 0

    if vertical > 0 and horizontal > 0:
        return "Quadrant 1"
    elif vertical > 0 and horizontal < 0:
        return "Quadrant 2"
    elif vertical < 0 and horizontal < 0:
        return "Quadrant 3"
    elif vertical < 0 and horizontal > 0:
        return "Quadrant 4"
    elif vertical > 0:
        return "North"
    elif vertical < 0:
        return "South"
    elif horizontal > 0:
        return "East"
    elif horizontal < 0:
        return "West"
    else:
        return "Center"
