# Extended Kalman Filter for positon data
# import matplotlib.pyplot as plt
import numpy as np
# import sympy as sp

def norm(q):
    return q/np.linalg.norm(q)
    # check division by zero

def quat_propagration(quat, angular_rates, dt): # gets the next time step in the equation
    # maybe update to RK4 instead --> different NumMeth
    wx, wy, wz = angular_rates
    
    Omega = np.array([
        [0, -wx,-wy,-wz],
        [wx,  0, wz,-wy],
        [wy,-wz,  0, wz],
        [wz, wy,-wx,  0]
    ])

    # foward euler
    quat_next = quat + (0.5 * Omega @ quat * dt)
    quat_next = norm(quat_next)

    return quat_next

def quat_to_DCM(quat): # gets the DCM roation matrix from quat
    qw, qx, qy, qz = quat

    dcm = np.array([
        [2*(qw**2 + qx**2) - 1, 2*(qx*qy - qw*qz),     2*(qx*qz + qw*qy)],
        [2*(qx*qy + qw*qz),     2*(qw**2 + qy**2) - 1, 2*(qy*qz - qw*qx)],
        [2*(qx*qz - qw*qy),     2*(qy*qz + qw*qx),     2*(qw**2 + qz**2) - 1]
    ])

    return dcm

# for all state arrays they are expecting [positon,vel,quat] 1X12
def state_next(state, imu_data, dt): # gets next state array in time loop
    postion = state[0:2]
    velocity = state[3:6]
    quat = state[7:11]
    
    acceleration = imu_data[3:6]
    angular_rates = imu_data[0:2]

    quat_next = quat_propagration(quat, angular_rates, dt)
    quat_next = norm(quat_next)
    dcm = quat_to_DCM(quat)
    
    gravity = np.array([0,0,-9.81])
    # check if g is measured up or down (+ or -) and convention of IMU

    accl_inertial_frame = dcm @ acceleration + gravity

    postion_next = postion + velocity*dt + 0.5*accl_inertial_frame*dt**2
    velocity_next = velocity + accl_inertial_frame*dt

    return np.concatenate([postion_next, velocity_next, quat_next])

def state_Jacobian(state, dt): # computes jacobian matrix which relates current state with next state in continuous time
    # numerical jacobian
    return 

def EKF_step(state, P, GPS_data, Q, R, dt): 
    # estimate step
    state_pred = state_next(state, dt)
    A = state_Jacobian(state, dt) # jacobian matrix
    P_pred = A @ P @ A.T + Q # error covarience
        # Q is error covarience noise of IMU
    
    # define H as Ident 3x3 for now bc idk what esle to do
    H = np.zeros((3, len(state)))
    H[:, 0:3] = np.eye(3)
    
    # measurement step
    K_gain = P_pred @ H.T @ np.linalg.inv(H @ P_pred @ H.T + R)
        # R is err covarience of GPS, less=trust mearurment more
    z_pred = state_pred[0:2]
    z_measured = GPS_data[0:2] # read x,y,z
    state_updated = state_pred + K_gain @ (z_measured - z_pred)

    # normalize quat
    state_updated[7:11] = norm(state_updated[7:11])

    P_updated = (np.eye(len(state)) -  K_gain @ H) @ P_pred

    return state_updated, P_updated