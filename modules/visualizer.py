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


    fig, axs = plt.subplots(2, 2, constrained_layout=True)
    fig.suptitle(title)

    axs[0][0].plot(time_array, job_progress_array, label="Job Progress", linewidth=0.5)
    axs[0][0].text(time_array[-1]/2, 20, f"Execution time: {time_array[-1]:.2f} seconds")
    axs[0][0].set_ylabel("Job Progress (%)")
    axs[0][0].set_xlabel("Time(s)")
    axs[0][0].legend()
    axs[0][0].grid(True)

    axs[0][1].plot(time_array, replicas_array, label="Replicas", linewidth=0.5)
    axs[0][1].set_xlabel("Time(s)")
    axs[0][1].legend()
    axs[0][1].grid(True)
    
    axs[1][0].plot(time_array, setpoint_array, color='green', linestyle='dashed', label="Setpoint(reference)", linewidth=0.5)
    axs[1][0].set_xlabel("Time (s)")
    axs[1][0].legend()
    axs[1][0].grid(True)

    axs[1][1].plot(time_array, error_array, label="Error", linewidth=0.5)
    axs[1][1].set_xlabel("Time (s)")
    axs[1][1].legend()    
    axs[1][1].grid(True)

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

    fig, axs = plt.subplots(3, 1, constrained_layout=True)
    fig.suptitle(title)

    axs[0].set_title("Input and output fluxes")
    axs[0].plot(time_array, input_flux_array, label="Input Flux", linewidth=0.5)
    axs[0].plot(time_array, output_flux_array, color='green', linestyle='dashed', label="Output Flux", linewidth=0.5)
    axs[0].set_ylabel("Items per second")    
    axs[0].set_xlabel("Time(s)")
    axs[0].grid(True)
    axs[0].legend()
    
    axs[1].set_title("Replicas")
    axs[1].plot(time_array, replicas_array, label="Replicas", linewidth=0.5)
    axs[1].set_xlabel("Time(s)")
    axs[1].grid(True)
    axs[1].legend()

    axs[2].set_title("Error")
    axs[2].plot(time_array, error_array, color="red", label="Error", linewidth=0.5)
    axs[2].set_xlabel("Time(s)")
    axs[2].grid(True)
    axs[2].legend()

    plt.show()