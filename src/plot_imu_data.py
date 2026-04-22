import matplotlib.pyplot as plt
import pandas as pd

# inputs to function are stings
def plot_imu_data(csv_file):
    # read data
    data = pd.read_csv(csv_file)

    time = data["Time"]
    
    ax = data["Ax"]
    ay = data["Ay"]
    az = data["Az"]
    
    gx = data["Wx"]
    gy = data["Wy"]
    gz = data["Wz"]
    
    roll = data["roll"]
    pitch = data["pitch"]
    yaw = data["yaw"]

    plt.figure()
    plt.plot(time, ax, "r", label="X")
    plt.plot(time, ay, "r", label="Y")
    plt.plot(time, az, "r", label="Z")
    # accel plot params     
    plt.title("Acceleration")
    plt.xlabel("Time")
    plt.ylabel("Acceleration")
    plt.legend()
    plt.grid()

    plt.figure()
    plt.plot(time, gx, "r", label="X")
    plt.plot(time, gy, "g", label="Y")
    plt.plot(time, gz, "b", label="Z")
    # gyro plot params
    plt.title("Gyroscope")
    plt.xlabel("Time")
    plt.ylabel("Rotation")
    plt.legend()
    plt.grid()

    plt.figure()
    plt.plot(time, roll, "r", label="Roll")
    plt.plot(time, pitch, "g", label="Pitch")
    plt.plot(time, yaw, "b", label="Yaw")
    # angle plot params
    plt.title("Euler Angles")
    plt.xlabel("Time")
    plt.ylabel("Angle")
    plt.legend()
    plt.grid()

    plt.show()