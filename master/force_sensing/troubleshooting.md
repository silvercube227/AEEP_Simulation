Common bug fixes:
1.Before starting, make sure all the wires are plugged in properly because they’re finicky

2. If you see only zeros being output for the quadrant detection/flex sensors, go into force_reader_threading.py and uncomment the two lines that say print(inLine) and the time.sleep and run it. If the calibration values are super low or infinity, then the wires are not set up properly. The values should be super high.

3. Force_reader_threding and conductive-reader_threading have their own main functions that you can run individually to determine which port the respective arduinos are connected to, run those individually first to change port.

4. The system takes 10 ish seconds to calibrate before it starts reading - you’ll know because the first samples will all be identical and then itll start changing when it starts calibrating

5. the code on the two raspberry pi’s I had to edit manually because GitHub wasn’t working, so if there’s any syntax error/runtime error message me and send me a text and a photo of the file that the error message says the error is in if you can’t find it

6. If for some reason the values are not returning consistently for the conductive sheet (i.e. you see random jumps when testing and zeros when you’re pressing down), check the timeout rate in the serial_loop function in conductive_sheet_threading and make sure its not too low