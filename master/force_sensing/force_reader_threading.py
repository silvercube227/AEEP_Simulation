import serial
import time
import re
from quadrant_detection import determine_quadrant
from threading import Thread, Lock
#read regex pattern
pattern = re.compile(r"(\w+):(-?\d+(?:\.\d+)?)")

latest_angles = (0.0, 0.0, 0.0, 0.0)
#parses data
def parse(data: str):
    matches = pattern.findall(data)
    return {d: float(v) for d, v in matches}

def serial_loop(port='/dev/arduino_flex', baud_rate=9600):
    """ Continuously read serial and update latest_angles """
    global latest_angles, stop_flag
    try:
        with serial.Serial(port, baud_rate, timeout=0.5) as arduino:
            while True:
                inline = arduino.readline().decode('utf-8', errors="ignore").strip()
                #print(inline)
                #time.sleep(0.2)
                if not inline:
                    continue
                dire = parse(inline)
                if dire:
                    north = dire.get("North", 0.0)
                    south = dire.get("South", 0.0)
                    east = dire.get("East", 0.0)
                    west = dire.get("West",0.0)
            
                    latest_angles = (north, south, east, west)
    except Exception as e:
        print(f"[Serial error] {e}")

def start_serial_thread(port='/dev/arduino_flex', baud_rate=9600):
    thread = Thread(target=serial_loop, args=(port, baud_rate), daemon=True)
    thread.start()
    return thread

def get_latest_angles():
    return latest_angles

def stop_serial_thread():
    """ Signal the serial loop to stop """
    global stop_flag
    stop_flag = True
def scan_angles():
    while True:
        n,s,e,w = get_latest_angles()
        quadrant = determine_quadrant(n,s,e,w)
        print(n,s,e,w, quadrant)
        time.sleep(0.2)

if __name__ == "__main__":
    start_serial_thread()
    scan_angles()
