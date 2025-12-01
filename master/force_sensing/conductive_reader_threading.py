import serial
import time
import re
from threading import Thread

# Regex pattern to parse "Raw: 512  V: 2.502  %: 45.3"
pattern = re.compile(r"Rel(\d+):\s*([\d.]+)")

latest_sheet = [0.0] * 15

stop_flag = False 

def parse(data: str):
    matches = re.findall(r"Rel(\d+):\s*([\d.]+)", data)
    return {int(index): float(value) for index, value in matches}


def serial_loop(port='/dev/arduino_conductive', baud_rate=115200):
    """ Continuously read serial and update latest_sheet """
    global latest_sheet, stop_flag
    try:
        with serial.Serial(port, baud_rate, timeout=0.01) as arduino:
            time.sleep(2)
            while not stop_flag:
                inline = arduino.readline().decode('utf-8', errors="ignore").strip()
                if not inline:
                    continue
                parsed = parse(inline)
                if parsed:
                    latest_sheet = [parsed.get(i, 0.0) for i in range(15)]
    except Exception as e:
        print(f"[Sheet Serial error] {e}")


def start_serial_thread(port='/dev/arduino_conductive', baud_rate=115200):
    """ Start the serial reading thread """
    global stop_flag
    stop_flag = False
    thread = Thread(target=serial_loop, args=(port, baud_rate), daemon=True)
    thread.start()
    return thread


def get_latest_sheet():
    """ Get the most recent conductive sheet values (raw, voltage, percent) """
    return latest_sheet


def stop_serial_thread():
    """ Signal the serial loop to stop """
    global stop_flag
    stop_flag = True
    
def scan_angles():
    while True:
        print(latest_sheet)
        time.sleep(0.2)

if __name__ == "__main__":
    start_serial_thread()
    scan_angles()
