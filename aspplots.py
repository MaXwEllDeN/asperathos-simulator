import matplotlib.pyplot as plt
import numpy as np

def generate_plots(simulation_data):
    time_array = []
    jp_array = []
    rp_array = []
    jpps_array = []

    for item in simulation_data:
        time_array.append(item["time"])
        jp_array.append(item["job_progress"])
        rp_array.append(item["replicas"])
        jpps_array.append(item["avg_jpps"])

    """
    model = {
        "time": execution_time,
        "job_progress": progress,
        "jpps": jpps,
        "jpps_error": jpps_error,        
        "replicas": replicas,
        "control_action": control_action
    }
    """

    plt.figure("Experiment Data")
    plt.subplot(3, 1, 1)
    plt.plot(time_array, jp_array, label='jobprogress')
    
    plt.title("Job Progress")
    plt.legend()


    plt.subplot(3, 1, 2)
    plt.plot(time_array, rp_array, label='replicas')

    plt.title("Control Action")
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(time_array, jpps_array, label='JP/s')
    
    plt.title("Job progress per second")
    plt.legend()

    plt.show()
