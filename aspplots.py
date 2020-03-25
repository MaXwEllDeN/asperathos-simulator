import matplotlib.pyplot as plt
import numpy as np

def generate_plots(simulation_data):
    time_array = []
    job_progress_array = []
    speed_array = []
    error_array = []
    replicas_array = []
    setpoint_array = []

    for item in simulation_data:
        time_array.append(item["time"])
        job_progress_array.append(item["job_progress"])
        speed_array.append(item["jpps"])
        error_array.append(item["error"])
        replicas_array.append(item["replicas"])
        setpoint_array.append(item["setpoint"])

    plt.figure("Simulation Data")

    plt.subplot(3, 1, 1)
    plt.plot(time_array, job_progress_array, label='Job Progress')
    
    plt.title("Job Progress")
    plt.legend()
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(time_array, speed_array, label='Speed')
    plt.plot(time_array, setpoint_array, color='green', linestyle='dashed', label='Speed Setpoint')
    plt.plot(time_array, replicas_array, color='orange', linestyle='dashed', label="Replicas")

    plt.title("JP/s")
    plt.legend()
    plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(time_array, error_array, label='Error')

    plt.title("Error")
    plt.legend()
    plt.grid(True)

    plt.show()
