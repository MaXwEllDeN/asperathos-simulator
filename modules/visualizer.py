import matplotlib.pyplot as plt
import numpy as np

def batch(title, data):
    time_array = []
    job_progress_array = []
    error_array = []
    replicas_array = []
    setpoint_array = []

    for item in data:
        time_array.append(item["time"])
        job_progress_array.append(item["job_progress"])
        error_array.append(item["error"])
        replicas_array.append(item["replicas"])
        setpoint_array.append(item["setpoint"])

    plt.figure(title)
    plt.suptitle(title)    
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)

    plt.subplot(2, 2, 1)
    plt.plot(time_array, job_progress_array, label="Job Progress")
    plt.text(time_array[-1]/2, 20, f"Execution time: {time_array[-1]:.2f} seconds")
    plt.ylabel("Job Progress (%)")
    
    plt.legend()
    plt.xlabel("Time (s)")
    plt.grid(True)

    plt.subplot(2, 2, 2)
    plt.plot(time_array, replicas_array, label="Replicas")

    plt.legend()
    plt.xlabel("Time (s)")
    plt.grid(True)

    
    plt.subplot(2, 2, 3)
    plt.plot(time_array, setpoint_array, color='orange', linestyle='dashed', label="Setpoint(reference)")

    plt.legend()
    plt.xlabel("Time (s)")
    plt.grid(True)

    plt.subplot(2, 2, 4)
    plt.plot(time_array, error_array, label="Error")

    plt.legend()
    plt.xlabel("Time (s)")
    plt.grid(True)

    plt.show()

def stream(title, data):
    time_array = []
    error_array = []
    replicas_array = []
    setpoint_array = []
    input_flux_array = []
    output_flux_array = []

    for item in data:
        time_array.append(item["time"])
        error_array.append(item["error"])
        input_flux_array.append(item["input_flux"])
        output_flux_array.append(item["output_flux"])
        replicas_array.append(item["replicas"])
        setpoint_array.append(item["setpoint"])

    plt.figure(title)
    plt.suptitle(title)    
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)

    plt.subplot(2, 2, 1)
    plt.plot(time_array, input_flux_array, label="Input Flux")
    plt.plot(time_array, output_flux_array, color='orange', linestyle='dashed', label="Output Flux")
    #plt.text(time_array[-1]/2, 20, f"Execution time: {time_array[-1]:.2f} seconds")
    plt.ylabel("Items per second")
    
    plt.legend()
    plt.xlabel("Time (s)")
    plt.grid(True)

    plt.subplot(2, 2, 2)
    plt.plot(time_array, replicas_array, label="Replicas")

    plt.legend()
    plt.xlabel("Time (s)")
    plt.grid(True)

    
    plt.subplot(2, 2, 3)
    plt.plot(time_array, setpoint_array, color='orange', linestyle='dashed', label="Setpoint(reference)")

    plt.legend()
    plt.xlabel("Time (s)")
    plt.grid(True)

    plt.subplot(2, 2, 4)
    plt.plot(time_array, error_array, label="Error")

    plt.legend()
    plt.xlabel("Time (s)")
    plt.grid(True)

    plt.show()