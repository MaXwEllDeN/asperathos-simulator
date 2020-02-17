import matplotlib.pyplot as plt
import numpy as np

def generate_plots(simulation_data):
    time_array = []
    jp_array = []
    rp_array = []
    avg_array = []
    completed_array = []

    for item in simulation_data:
        time_array.append(item["time"])
        jp_array.append(item["job_progress"])
        rp_array.append(item["replicas"])
        avg_array.append(item["avg_jpps"])
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
    """
    plt.subplot(3, 1, 2)
    plt.plot(time_array, rp_array, label='replicas')

    plt.title("Control Action")
    plt.legend()
    plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(time_array, jpps_array, label='JP/s')
    
    plt.title("Job progress per second")
    plt.legend()
    """

    avg_avg_jpps = []
    avg = sum(avg_array) / len(avg_array)

    for i in avg_array:
        avg_avg_jpps.append(avg)

    plt.subplot(3, 1, 3)

    plt.plot(time_array, avg_array, label='Avg j/s')
    plt.plot(time_array, avg_avg_jpps, color='orange', linestyle='dashed', label='Avg: {}'.format(avg))

    plt.title("Average jobs per second")
    plt.legend()
    plt.grid(True)

    plt.show()
