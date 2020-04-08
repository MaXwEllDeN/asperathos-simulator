import matplotlib.pyplot as plt
import numpy as np

def generate_plots(simulation_data):
    time_array = []
    job_progress_array = []
    speed_array = []
    replicas_array = []

    for item in simulation_data:
        time_array.append(item["time"])
        job_progress_array.append(item["job_progress"])
        speed_array.append(item["jpps"])
        replicas_array.append(item["replicas"])

    plt.figure("Experimental Data")
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)

    plt.subplot(2, 1, 1)
    plt.plot(time_array, job_progress_array, label="Job Progress")
    plt.text(time_array[-1]/2, 20, f"Execution time: {time_array[-1]} seconds")
    plt.ylabel("Job Progress (%)")
    
    plt.title("Experimental Data with step = {}".format(max(replicas_array)))
    plt.legend()
    plt.xlabel("Time (s)")
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(time_array, speed_array, label="Speed(JP/s)")
    plt.plot(time_array, replicas_array, color='orange', linestyle='dashed', label="Replicas")

    plt.legend()
    plt.grid(True)

    plt.legend()
    plt.xlabel("Time (s)")
    plt.grid(True)

    plt.show()
