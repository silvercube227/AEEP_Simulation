from force_reader_threading import get_latest_angles, start_serial_thread as start_force_thread, stop_serial_thread as stop_force_thread
from quadrant_detection import determine_quadrant
from conductive_reader_threading import get_latest_sheet, start_serial_thread as start_conductive_thread, stop_serial_thread as stop_conductive_thread
import time
import os
import shutil
import csv

start_force_thread()
start_conductive_thread()

def store_data(file_path, name):
    directory_path = "bootcamp_data/" + name
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    shutil.move(file_path, os.path.join(directory_path, os.path.basename(file_path)))
    

def scan_angles():
    new_file_1 = not os.path.exists("quadrant_log.csv")
    new_file_2 = not os.path.exists("force_log.csv")

    with open("quadrant_log.csv", "a", newline='') as f1, open("force_log.csv", "a", newline='') as f2:
        quadrant_writer = csv.writer(f1)
        force_writer = csv.writer(f2)

        if new_file_1:
            quadrant_writer.writerow(["timestamp", "quadrant", "bend_angle", "N", "S", "E", "W"])
        if new_file_2:
            force_writer.writerow(["timestamp", "force_Array"])

        while True:
            n, s, e, w = get_latest_angles()
            latest_sheet = get_latest_sheet()
            quadrant = determine_quadrant(n, s, e, w)
            timestamp = time.time()

            print(quadrant)
            print(latest_sheet)
            quadrant_writer.writerow([timestamp, quadrant, n, s, e, w])
            force_writer.writerow([timestamp, *latest_sheet])
            f1.flush()
            f2.flush()

            time.sleep(0.5)
        

if __name__ == "__main__":
    ID = "f1"
    try:
        scan_angles()
    except KeyboardInterrupt:
        store_data("quadrant_log.csv", ID)
        store_data("force_log.csv", ID)
