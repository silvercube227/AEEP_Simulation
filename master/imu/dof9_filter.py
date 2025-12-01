import numpy as np
import pandas as pd
import csv

#reads imu with madgwick filter - however an enhanced kalman filter may work better for IMU
class MadgwickFilter:
    def __init__(self, sample_period, beta=0.1):
        """
        Initializes the Madgwick filter.
        
        Parameters:
        -----------
        sample_period : float
            The sample period (in seconds) between measurements.
        beta : float
            The filter gain; higher beta gives more weight to the correction.
        """
        self.sample_period = sample_period
        self.beta = beta
        # Initialize quaternion: [q0, q1, q2, q3]
        self.q = np.array([1.0, 0.0, 0.0, 0.0])
        self.position = 0
    
    def update(self, gyro, accel, mag):
        """
        Update the filter with new sensor measurements.
        
        Parameters:
        -----------
        gyro : array-like, shape (3,)
            Gyroscope measurements (rad/s) as [gx, gy, gz].
        accel : array-like, shape (3,)
            Accelerometer measurements (in g or m/s^2, if gravity is present).
        mag : array-like, shape (3,)
            Magnetometer measurements.
            
        Returns:
        --------
        q : ndarray, shape (4,)
            The updated orientation quaternion.
        """
        q1, q2, q3, q4 = self.q

        # Normalize accelerometer measurement
        if np.linalg.norm(accel) == 0:
            return self.q  # avoid division by zero
        accel = accel / np.linalg.norm(accel)

        # Normalize magnetometer measurement
        if np.linalg.norm(mag) == 0:
            return self.q
        mag = mag / np.linalg.norm(mag)

        # Auxiliary variables to avoid repeated arithmetic
        _2q1 = 2.0 * q1
        _2q2 = 2.0 * q2
        _2q3 = 2.0 * q3
        _2q4 = 2.0 * q4
        _4q1 = 4.0 * q1
        _4q2 = 4.0 * q2
        _4q3 = 4.0 * q3
        _8q2 = 8.0 * q2
        _8q3 = 8.0 * q3
        q1q1 = q1 * q1
        q2q2 = q2 * q2
        q3q3 = q3 * q3
        q4q4 = q4 * q4
        q2q4 = q2 * q4

        # Reference direction of Earth's magnetic field
        hx = mag[0] * (q1q1 + q2q2 - q3q3 - q4q4) + 2.0 * mag[1] * (q2 * q3 - q1 * q4) + 2.0 * mag[2] * (q2 * q4 + q1 * q3)
        hy = 2.0 * mag[0] * (q2 * q3 + q1 * q4) + mag[1] * (q1q1 - q2q2 + q3q3 - q4q4) + 2.0 * mag[2] * (q3 * q4 - q1 * q2)
        _2bx = np.sqrt(hx * hx + hy * hy)
        _2bz = 2.0 * mag[0] * (q2 * q4 - q1 * q3) + 2.0 * mag[1] * (q3 * q4 + q1 * q2) + mag[2] * (q1q1 - q2q2 - q3q3 + q4q4)

        # Gradient descent algorithm corrective step
        f1 = _2q2 * q4 - _2q1 * q3 - accel[0]
        f2 = _2q1 * q2 + _2q3 * q4 - accel[1]
        f3 = 1.0 - _2q2 * q2 - _2q3 * q3 - accel[2]
        # Similarly, include terms that incorporate the magnetic field;
        # for brevity, we combine them into s1, s2, s3, s4 below.
        s1 = -_2q3 * (2.0 * q2q4 - _2q1 * q3 - accel[0]) + _2q2 * (2.0 * q1 * q2 + _2q3 * q4 - accel[1])
        s2 = _2q4 * (2.0 * q2q4 - _2q1 * q3 - accel[0]) + _2q1 * (2.0 * q1 * q2 + _2q3 * q4 - accel[1]) - 4.0 * q2 * (1.0 - 2.0 * q2q2 - 2.0 * q3q3 - accel[2])
        s3 = -_2q1 * (2.0 * q2q4 - _2q1 * q3 - accel[0]) + _2q4 * (2.0 * q1 * q2 + _2q3 * q4 - accel[1]) - 4.0 * q3 * (1.0 - 2.0 * q2q2 - 2.0 * q3q3 - accel[2])
        s4 = _2q2 * (2.0 * q2q4 - _2q1 * q3 - accel[0]) + _2q3 * (2.0 * q1 * q2 + _2q3 * q4 - accel[1])
        norm_s = np.linalg.norm([s1, s2, s3, s4])
        if norm_s == 0:
            norm_s = 1
        s1, s2, s3, s4 = s1 / norm_s, s2 / norm_s, s3 / norm_s, s4 / norm_s

        # Compute the rate of change of quaternion from gyroscope
        gx, gy, gz = gyro
        q_dot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - self.beta * s1
        q_dot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - self.beta * s2
        q_dot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - self.beta * s3
        q_dot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - self.beta * s4

        # Integrate to yield new quaternion
        q1 += q_dot1 * self.sample_period
        q2 += q_dot2 * self.sample_period
        q3 += q_dot3 * self.sample_period
        q4 += q_dot4 * self.sample_period
        q_new = np.array([q1, q2, q3, q4])
        # Normalize quaternion
        self.q = q_new / np.linalg.norm(q_new)
        return self.q

    def get_euler(self):
        """
        Returns the current orientation as Euler angles (yaw, pitch, roll) in degrees.
        """
        q = self.q
        # Yaw (z-axis rotation)
        yaw = np.arctan2(2*(q[0]*q[1] + q[2]*q[3]),
                         1 - 2*(q[1]*q[1] + q[2]*q[2]))
        # Pitch (y-axis rotation)
        pitch = np.arcsin(2*(q[0]*q[2] - q[3]*q[1]))
        # Roll (x-axis rotation)
        roll = np.arctan2(2*(q[0]*q[3] + q[1]*q[2]),
                          1 - 2*(q[2]*q[2] + q[3]*q[3]))
        return np.degrees(yaw), np.degrees(pitch), np.degrees(roll)
    
    def get_rotation_matrix(self):
        """
        Returns the 3x3 rotation matrix corresponding to the current quaternion.
        """
        q = self.q
        # Compute the rotation matrix elements
        r11 = 1 - 2*(q[2]**2 + q[3]**2)
        r12 = 2*(q[1]*q[2] - q[0]*q[3])
        r13 = 2*(q[1]*q[3] + q[0]*q[2])
        r21 = 2*(q[1]*q[2] + q[0]*q[3])
        r22 = 1 - 2*(q[1]**2 + q[3]**2)
        r23 = 2*(q[2]*q[3] - q[0]*q[1])
        r31 = 2*(q[1]*q[3] - q[0]*q[2])
        r32 = 2*(q[2]*q[3] + q[0]*q[1])
        r33 = 1 - 2*(q[1]**2 + q[2]**2)
        return np.array([[r11, r12, r13],
                         [r21, r22, r23],
                         [r31, r32, r33]])

    def calibrate_magnetometer(self, mag_data):
        calibrated_mag_data = np.zeros_like(mag_data)
        B = [109.06238802, 37.90448955, 125.2127988]
        A_inv = [[2.58891148, 0.03830976, -0.05865281],[0.03830976, 2.79695092, 0.03519644], [-0.05865281, 0.03519644, 2.72060039]]

        for i in range(mag_data.shape[0]):
            # Subtract hard iron bias
            mag_data[i] = mag_data[i] - B
            # Apply soft iron transformation
            calibrated_mag_data[i] = np.dot(mag_data[i], A_inv)
        return calibrated_mag_data

    def compute_position(self, data, beta, L):
        data = np.asarray(data)
        if data.size % 10 != 0:
            raise ValueError("Input array must have a length multiple of 10.")

        # Reshape to (N, 10)
        data = data.reshape(-1, 10)
        N = data.shape[0]

        dts = data[:, 0]
        if data.shape[0] == 1:
            accel_data = data[:, 1:4]
        else:
            accel_data = data[:, 1:4] - data[0, 1:4]
  # remove initial offset
        gyro_data = data[:, 4:7]
        mag_data = data[:, 7:10]

        mag_data = self.calibrate_magnetometer(mag_data)

        velocity = np.zeros((N, 3))
        position = np.zeros((N, 3))
        rod_tip_position = np.zeros((N, 3)) 
        quaternions = np.zeros((N,4))
        euler_angles = np.zeros((N,3))
        global_acc = np.zeros((N,3))

        
        madgwick = MadgwickFilter(sample_period=np.mean(dts), beta=beta)

        for i in range(N):
            dt = dts[i] if dts[i] > 0 else np.mean(dts)
            madgwick.sample_period = dt

            q = madgwick.update(gyro=gyro_data[i], accel=accel_data[i], mag=mag_data[i])
            quaternions[i] = q

            R = madgwick.get_rotation_matrix()
            global_acc = R @ accel_data[i]

            if i > 0:
                velocity[i] = global_acc * dt
                position[i] = 0.5 * global_acc * dt**2
            else:
                velocity[i] = velocity[i-1] + global_acc * dt
                position[i] = position[i-1] + velocity[i-1] * dt + 0.5 * global_acc * dt**2

            rod_offset = np.array([0,0,L])
            rod_global = R @ rod_offset

            rod_tip_position[i] = position[i] + rod_global

        return position[-1]

def read_imu_data(csv_path):
        """
        Generator that yields (gyro, accel, mag) tuples from a CSV with
        columns: Timestamp,Accel_X,Accel_Y,Accel_Z,Gyro_X,Gyro_Y,Gyro_Z,Mag_X,Mag_Y,Mag_Z
        """
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # parse into numpy arrays
                accel = np.array([
                    float(row['Accel_X']),
                    float(row['Accel_Y']),
                    float(row['Accel_Z'])
                ])
                gyro = np.array([
                    float(row['Gyro_X']),
                    float(row['Gyro_Y']),
                    float(row['Gyro_Z'])
                ])
                mag = np.array([
                    float(row['Mag_X']),
                    float(row['Mag_Y']),
                    float(row['Mag_Z'])
                ])
                yield gyro, accel, mag

if __name__ == "__main__":
    csv_path = '50cm_trial2_extracted.csv'

    # 1) Load CSV into a (N×10) array [Timestamp, Accel_X–Z, Gyro_X–Z, Mag_X–Z]
    import pandas as pd
    df = pd.read_csv(csv_path)

    # ensure columns are in the right order
    cols = ['Timestamp',
            'Accel_X','Accel_Y','Accel_Z',
            'Gyro_X','Gyro_Y','Gyro_Z',
            'Mag_X','Mag_Y','Mag_Z']
    data_2d = df[cols].to_numpy()            # shape=(N,10)

    # 2) Flatten to 1-D for compute_position
    data_flat = data_2d.flatten()            # length = N*10

    # 3) Instantiate filter & compute position
    madgwick = MadgwickFilter(
        sample_period = df['Timestamp'].diff().mean(),  # average Δt
        beta          = 0.1
    )

    # L is the rod length in meters
    L = 0

    final_pos = madgwick.compute_position(
        data = data_flat,
        beta = madgwick.beta,
        L    = L
    )

    print("Final IMU-derived position:", final_pos)
