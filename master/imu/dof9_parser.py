import re

def parse(line):
    """
    Parses a line of IMU data and extracts time, acceleration, gyroscope,
    and magnetometer readings.

    The expected format of the input string is something like:
    "0.069569 s Accel X: 0.14 Y: 0.73 Z: 0.26 m/s^2 Mag X: -5.70 Y: 7.20 Z: -8.00uT Gyro X: -0.00 Y: -0.01 Z: 0.01radians/s"

    Returns:
        Tuple containing:
        dt (float): timestamp in seconds
        ax, ay, az (float): acceleration in m/s^2
        gx, gy, gz (float): angular velocity in radians/s
        mx, my, mz (float): magnetic field strength in microteslas
    """

    # Compile regular expression patterns for each type of data
    pattern_time = re.compile(r'(\d+\.\d+) s')
    pattern_accel = re.compile(r'Accel X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+) m/s\^2')
    pattern_gyro = re.compile(r'Gyro X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+)radians/s')
    pattern_mag = re.compile(r'Mag X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+)uT')

    # Search for timestamp
    match_time = pattern_time.search(line)
    if match_time:
        current_time = float(match_time.group(1))

    # Search for acceleration values
    match_accel = pattern_accel.search(line)
    if match_accel:
        dt = current_time
        ax = float(match_accel.group(1))
        ay = float(match_accel.group(2))
        az = float(match_accel.group(3))

    # Search for gyroscope values
    match_gyro = pattern_gyro.search(line)
    if match_gyro:
        gx = float(match_gyro.group(1))
        gy = float(match_gyro.group(2))
        gz = float(match_gyro.group(3))

    # Search for magnetometer values
    match_mag = pattern_mag.search(line)
    if match_mag:
        mx = float(match_mag.group(1))
        my = float(match_mag.group(2))
        mz = float(match_mag.group(3))

    # Return all parsed values
    return dt, ax, ay, az, gx, gy, gz, mx, my, mz

# Example usage
# dof9_line = "0.069569 s Accel X: 0.14 Y: 0.73 Z: 0.26 m/s^2 Mag X: -5.70 Y: 7.20 Z: -8.00uT Gyro X: -0.00 Y: -0.01 Z: 0.01radians/s"
# parse(dof9_line)
