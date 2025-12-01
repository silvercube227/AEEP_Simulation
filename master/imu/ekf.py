import numpy as np
import pandas as pd
from filterpy.kalman import ExtendedKalmanFilter

# ——— quaternion utilities ———
def normalize_quat(q):
    return q / np.linalg.nxorm(q)

def quaternion_to_rotation_matrix(q):
    w, x, y, z = q
    return np.array([
        [1 - 2*(y*y + z*z),   2*(x*y - z*w),     2*(x*z + y*w)],
        [2*(x*y + z*w),       1 - 2*(x*x + z*z), 2*(y*z - x*w)],
        [2*(x*z - y*w),       2*(y*z + x*w),     1 - 2*(x*x + y*y)]
    ])

# ——— measurement & heading models ———
def acc_mag_prediction(q, g_ref=np.array([0,0,1]), m_ref=np.array([1,0,0])):
    R = quaternion_to_rotation_matrix(q)
    g_b = R.T @ g_ref
    m_b = R.T @ (m_ref/np.linalg.norm(m_ref))
    return np.hstack((g_b, m_b))

def H_jacobian(x):
    q = x[0:4]
    eps = 1e-6
    H = np.zeros((6, x.shape[0]))
    for i in range(4):
        dq = np.zeros(4); dq[i] = eps
        zp = acc_mag_prediction(normalize_quat(q + dq))
        zm = acc_mag_prediction(normalize_quat(q - dq))
        H[:, i] = (zp - zm) / (2 * eps)
    return H

def tilt_compensated_heading(mag, q):
    R_nav = quaternion_to_rotation_matrix(q)
    m_nav = R_nav @ mag
    return np.arctan2(m_nav[1], m_nav[0])

# ——— EKF with gyro-bias & compass corrections ———
class OrientationBiasEKF:
    def __init__(self):
        self.ekf = ExtendedKalmanFilter(dim_x=7, dim_z=6)
        self.ekf.x = np.hstack((np.array([1.,0.,0.,0.]), np.zeros(3)))
        self.ekf.P = np.eye(7) * 0.01
        Q = np.eye(7) * 1e-5
        Q[4:,4:] *= 1e-4
        self.ekf.Q = Q
        self.R_accmag = np.eye(6) * 1e-2
        self.R_yaw    = np.array([[1e-3]])

    def predict(self, gyro, dt):
        bg = self.ekf.x[4:7]
        wx, wy, wz = gyro - bg
        Omega = np.array([
            [0,   -wx, -wy, -wz],
            [wx,   0,   wz, -wy],
            [wy,  -wz,  0,   wx],
            [wz,   wy, -wx,  0  ]
        ])
        F = np.eye(7)
        F[0:4,0:4] = np.eye(4) + 0.5 * dt * Omega
        self.ekf.F = F
        self.ekf.predict()

    def update(self, accel, mag):
        # full accel+mag update
        a_n = accel/np.linalg.norm(accel)
        m_n = mag/np.linalg.norm(mag)
        z_am = np.hstack((a_n, m_n))
        self.ekf.R = self.R_accmag
        self.ekf.update(z_am,
                        HJacobian=lambda x: H_jacobian(x),
                        Hx=lambda x: acc_mag_prediction(x[0:4]))
        self.ekf.x[0:4] = normalize_quat(self.ekf.x[0:4])
        # yaw-only compass update
        q   = self.ekf.x[0:4]
        yaw_meas = tilt_compensated_heading(mag, q)
        def h_yaw(x): return np.array([ tilt_compensated_heading(mag, x[0:4]) ])
        def H_yaw(x):
            hy = np.zeros((1,7)); eps=1e-6
            for i in range(4):
                dx = np.zeros(7); dx[i]=eps
                hp = tilt_compensated_heading(mag, normalize_quat(x[0:4]+dx[0:4]))
                hm = tilt_compensated_heading(mag, normalize_quat(x[0:4]-dx[0:4]))
                hy[0,i] = (hp-hm)/(2*eps)
            return hy
        self.ekf.R = self.R_yaw
        self.ekf.update(np.array([yaw_meas]), HJacobian=H_yaw, Hx=h_yaw)
        self.ekf.x[0:4] = normalize_quat(self.ekf.x[0:4])
        return self.ekf.x[0:4]

# ——— Main integration ———
#replace file with your own testing data
df = pd.read_csv('testing/new_imu/Trial1_Y_extracted.csv')
n  = len(df)
Q = np.zeros((n,4))
V = np.zeros((n,3))
P = np.zeros((n,3))

orient_ekf = OrientationBiasEKF()
for i in range(1, n):
    dt   = df.at[i,'Timestamp'] - df.at[i-1,'Timestamp']
    gyr  = df.loc[i, ['Gyro_X','Gyro_Y','Gyro_Z']].values
    acc  = df.loc[i, ['Accel_X','Accel_Y','Accel_Z']].values
    mag  = df.loc[i, ['Mag_X','Mag_Y','Mag_Z']].values
    # update orientation
    orient_ekf.predict(gyr, dt)
    q    = orient_ekf.update(acc, mag)
    Q[i] = q
    # integrate in world frame
    Rwb       = quaternion_to_rotation_matrix(q)
    acc_world = Rwb.dot(acc) - np.array([0,0,9.81])
    V[i] = V[i-1] + acc_world * dt
    P[i] = P[i-1] + V[i] * dt
    # print position at each sample
    print(f"Time {df.at[i,'Timestamp']:.3f}s -> Position: {P[i].round(4)} m")

