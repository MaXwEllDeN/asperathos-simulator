#Calculate parameters
import numpy as np
import matplotlib.pyplot as plt

files = [
    # 0.059751 0.059751
    "/home/maxwell/workspace/lsd/repos/asperathos-simulator/experiments/stream/17h15m11s 24-03-2021.csv",
    "/home/maxwell/workspace/lsd/repos/asperathos-simulator/experiments/stream/17h00m49s 25-03-2021.csv",
    # 0.094771 0.094771
]

def rise_time(t, u, y, setpoint=0):
    t_init_step = -1
    t_rise = 0
    u_init = u[0]
    
    step_start = 0

    for index in range(len(y)):
        if t_init_step == -1 and u[index] > u_init:
            t_init_step = t[index]
            step_start = index

        if t_init_step != -1 and y[index] >= setpoint:
            t_rise = t[index]
            break

    return t_rise - t_init_step, step_start

def overshoot(y, setpoint):
    return max(y)

def settling_time(t, y, setpoint, step_start):
    error = abs(y - setpoint)
    peak_e = max(y)
    settling_threshold = 0.5

    for index in range(len(y) - 1, step_start, -1):

        if error[index] >= peak_e * settling_threshold :
            return t[index] - t[step_start], index

    return -1, 0

if __name__ == "__main__":  
    setpoint = 3

    for file_name in files:
        raw_data = np.genfromtxt(file_name, delimiter=",")

        t = raw_data[1:-4, 0]
        u = raw_data[1:-4, 1]
        y = raw_data[1:-4, 2]

        print("--------------------")
        tr, step_start = rise_time(t, u, y, setpoint)
        ts, step_final = settling_time(t, y, setpoint, step_start)

        print("Rise time: %.2f" % tr)
        print("Settling time: %.2f" % ts)

        fig = plt.figure()
        plt.plot(t, y)
        plt.plot(t, u, "--", label="Réplicas")
        plt.plot(t, np.ones(len(t))*setpoint)
        plt.plot(t[step_start], 0,'go', label="Step start")
        plt.plot(t[step_final], 0,'ro', label="Step final")
        plt.legend()
        plt.grid()
        plt.show()
