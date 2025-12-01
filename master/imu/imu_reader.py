import serial
import time
import re

def parse(line):
    """
    Parses a single line of text from the Arduino serial output to extract
    accelerometer, gyroscope, and magnetometer data.

    Parameters:
        line (str): A string containing IMU sensor readings from the Arduino.

    Returns:
        tuple: A 9-element tuple containing float values in the order:
               (ax, ay, az, gx, gy, gz, mx, my, mz)

    Raises:
        ValueError: If any of the sensor values are missing or can't be parsed.
    """
    
    # Regular expressions to extract data from the line
    pattern_accel = re.compile(r'Accel X:\s*(-?\d+(?:\.\d+)?)\s*Y:\s*(-?\d+(?:\.\d+)?)\s*Z:\s*(-?\d+(?:\.\d+)?)\s*m/s\^2')
    pattern_gyro = re.compile(r'Gyro X:\s*(-?\d+(?:\.\d+)?)\s*Y:\s*(-?\d+(?:\.\d+)?)\s*Z:\s*(-?\d+(?:\.\d+)?)\s*radians/s')
    pattern_mag = re.compile(r'Mag X:\s*(-?\d+(?:\.\d+)?)\s*Y:\s*(-?\d+(?:\.\d+)?)\s*Z:\s*(-?\d+(?:\.\d+)?)\s*uT')


    # Initialize all values to None
    ax = ay = az = gx = gy = gz = mx = my = mz = None

    #print(f"Parsing line: {line}")
    # Extract acceleration data
    match_accel = pattern_accel.search(line)
    #print(f"Accel match: {match_accel}")
    if match_accel:
        ax = float(match_accel.group(1))
        ay = float(match_accel.group(2))
        az = float(match_accel.group(3))

    # Extract gyroscope data
    match_gyro = pattern_gyro.search(line)
    if match_gyro:
        gx = float(match_gyro.group(1))
        gy = float(match_gyro.group(2))
        gz = float(match_gyro.group(3))

    # Extract magnetometer data
    match_mag = pattern_mag.search(line)
    if match_mag:
        mx = float(match_mag.group(1))
        my = float(match_mag.group(2))
        mz = float(match_mag.group(3))

    # Check if any values are still None (i.e., failed parsing)
    if None in [ax, ay, az, gx, gy, gz, mx, my, mz]:
        #If values are none initialize all to 0
        print("Failed to parse all values, initializing to 0")
        ax = 0
        ay = 0
        az = 0
        gx = 0
        gy = 0
        gz = 0
        mx = 0
        my = 0
        mz = 0
    

    return ax, ay, az, gx, gy, gz, mx, my, mz


def printlst(lst):
    """
    Utility function to print each element in a list on a new line.

    Parameters:
        lst (list): The list of elements to print.
    """
    for e in lst:
        print(e)


def read_imu_data(port='COM6', baud_rate=115200):
    """
    Connects to an Arduino device over a serial port and reads one line of IMU data.

    Parameters:
        port (str): The serial port to which the Arduino is connected (default is 'COM6').
        baud_rate (int): The baud rate for serial communication (default is 115200).

    Returns:
        tuple: A 9-element tuple containing float values of IMU readings in the order:
               (ax, ay, az, gx, gy, gz, mx, my, mz)
    """
    
    # Open serial connection to the Arduino
    with serial.Serial(port, baud_rate) as arduino:
        # Wait for connection to initialize
        time.sleep(2)

        # Clear any initial buffer noise
        arduino.reset_input_buffer()

        # Read a line from serial, decode to string and strip trailing newline
        inline = arduino.readline().decode('utf-8', errors="ignore").rstrip()

        # Parse the IMU data from the received line
        ax, ay, az, gx, gy, gz, mx, my, mz = parse(inline)

        return ax, ay, az, gx, gy, gz, mx, my, mz


def main():
    """
    Main function to run the IMU data reading process.
    You can modify this to loop or log data as needed.
    """
    try:
        data = read_imu_data()
        print("IMU Data (ax, ay, az, gx, gy, gz, mx, my, mz):")
        printlst(data)
    except Exception as e:
        print(f"Error reading IMU data: {e}")


if __name__ == "__main__":
    main()
