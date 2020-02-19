import matplotlib.pyplot as plt
import numpy as np

def generate_plots(simulation_data):
    time_array = []
    jp_array = []
    avg_array = []
    setpoint_array = []
    avg_setpoint_array = []
    completed_array = []

    for item in simulation_data:
        time_array.append(item["time"])
        jp_array.append(item["job_progress"])
        avg_array.append(item["avg_jpps"])
        setpoint_array.append(item["setpoint"])
        avg_setpoint_array.append(item["avg_setpoint"])
        completed_array.append(item["completed"])


    plt.figure("Experiment Data")

    plt.subplot(3, 1, 1)
    plt.plot(time_array, jp_array, label='jobprogress')
    
    plt.title("Job Progress")
    plt.legend()
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(time_array, completed_array, label='completed jobs')

    plt.title("Competed jobs")
    plt.legend()
    plt.grid(True)

    avg_avg_jpps = []
    avg = sum(avg_array) / len(avg_array)

    for i in avg_array:
        avg_avg_jpps.append(avg)

    plt.subplot(3, 1, 3)

    plt.plot(time_array, avg_array, label='Avg JP/s')
    plt.plot(time_array, avg_avg_jpps, color='orange', linestyle='dashed', label='Avg: {}'.format(avg))
    plt.plot(time_array, avg_setpoint_array, color='green', linestyle='dashed', label='Avg JP/s setpoint')

    plt.title("Average jobs per second")
    plt.legend()
    plt.grid(True)

    plt.show()
