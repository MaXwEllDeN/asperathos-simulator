#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import argparse

from os import walk
from math import ceil, isnan

def detect_steps(execution):
    steps = []

    last_replicas = None
    last_output = None
    step_started = None
    identifying_delay = False

    for row in execution:
        replicas = row[1]
        if isnan(replicas):
            continue

        output = ceil(row[2])
        timestamp = row[0]

        if last_replicas is None:
            last_replicas = replicas
            last_output = output
            step_started = timestamp
            continue

        if replicas > last_replicas:
            #print(f"[{timestamp}] Step at {row[0]}s, from {last_replicas} to {replicas} replicas.")
            last_replicas = replicas
            step_started = timestamp
            last_output = ceil(output)
            identifying_delay = True

        if identifying_delay and output > last_output:
            identifying_delay = False
            #print(f"[{timestamp}] Took {timestamp - step_started} second(s) to increase output flux from {last_output} items/s to {output} items/s.")
            #(duration, size)
            step = (timestamp - step_started, output - last_output)
            steps.append(step)

    return steps

def load_data(dir):
    _, _, filenames = next(walk(dir))
    filenames.remove("temp.csv")

    executions = []

    for file_name in filenames:
        #timestamp, replicas, real_output_flux, input_flux, error
        raw_data = np.genfromtxt(f"{dir}/{file_name}", delimiter=",")
        executions.append(raw_data)

    return executions

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="folder containng execution data.")
    args = parser.parse_args()

    data = load_data(args.folder)


    fig, axs = plt.subplots(3, 1, constrained_layout=True)
    fig.suptitle("Executions validation")
    fig.set_figwidth(20)
    fig.set_figheight(10)

    counter = 1
    for execution in data:
        time_array = []
        output_flux_array = []
        replicas_array = []

        error_array = []

        detected_steps = detect_steps(execution)
        print(detected_steps)

        for row in execution:
            time_array.append(row[0])
            output_flux_array.append(row[2])
            replicas_array.append(row[1])
            error_array.append(row[4])

        axs[0].plot(time_array, output_flux_array, linestyle='dashed', label=f"Output Flux {counter}", linewidth=0.5)
        axs[1].plot(time_array, replicas_array, label="Replicas", linewidth=0.5)    
        axs[2].plot(time_array, error_array, label="Error", linewidth=0.5)
        counter += 1

    axs[0].set_title("Input and output fluxes")
    axs[0].set_ylabel("Items per second")    
    axs[0].set_xlabel("Time(s)")
    axs[0].grid(True)
    #axs[0].legend()
     
    axs[1].set_title("Replicas")
    axs[1].set_xlabel("Time(s)")
    axs[1].grid(True)
    #axs[1].legend()

    axs[2].set_title("Error")
    axs[2].set_xlabel("Time(s)")
    axs[2].grid(True)
    #axs[2].legend()

    plt.show()