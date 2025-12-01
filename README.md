# AEEP_Simulation
This repository contains code for an AEEP simulation program. The repository is structured as follows:
folder bootcamp_data:
    * This folder contains all the data we collected during the simulation bootcamp, including timestamp marked data for one expert. EA6 contains the best data

folder master:
    *folder arduino - contains arduino code for flex sensor reading, IMU reading, and conductive sheet reading. 5/10/14/15SensorControl is used for testing various numbers of sensors.

    *folder force_sensing - contains code for force sensing and quadrant detection 
        *conductive_reader_threading.py reads code for conductive sheets
        *force_analysis.py is primarily used for the minimap - changes color of minimap based on force applied
        *force_main.py - ALL FORCE SENSING IS RUN THROUGH THIS FILE - if you are testing force sensing, run this
        *force_process.py - contains code that processes and plots data gathered
        *force_reader_threading.py - threaded flex sensor reader
        *quadrant_detection.py - code that determines which quadrant surgeon is in based on flex sensor readings
        *quadrant_process.py - plots and displays quadrants by frequency based on data
        *troubleshooting.md - IMPORTANT, contains common bugs and how to fix them
    
    *folder imu - contains code for IMU/movement detection
        *bph_mold_combined.stl - 3d render of prostate used for minimap
        *dof9_filter.py - madgwick filter to read IMU data and compute position
        *dof9_parser.py - parses IMU readings for IMU with 9 degrees of freedom
        *ekf.py - enhanced kalman filter - haven't fully tested for position tracking but is a logical next step
        *imu_reader.py - parse imu readings for IMU
    
    *main.py - creaets and displays the minimap, combines both force sensing and IMU reading. This file currently does not work because of codebase refactoring. Work on this last.
