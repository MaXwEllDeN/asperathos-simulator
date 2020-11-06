import glob
import numpy as np
import scipy.stats
from numpy import genfromtxt
import matplotlib.pyplot as plt

LARGER_STEP = 12
EXP_DIR327 = f"/home/maxwell/workspace/lsd/repos/asperathos-simulator/experiments/batch/wl327"
EXP_DIR800 = f"/home/maxwell/workspace/lsd/repos/asperathos-simulator/experiments/batch/wl800"

# Execution times on simulator
data_simu_800 = [164, 84, 58, 46, 38, 28, 34, 28, 26, 24, 24, 24]
data_simu_327 = [70, 38, 26, 22, 20, 16, 16, 16, 16, 16, 16, 16]

# width of the bars
barWidth = 0.1

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return h

def get_step_dataset(path):
    files = [f for f in glob.glob(path + "/*.csv", recursive=True)]

    execution_times = []

    for f in files:
        my_data = genfromtxt(f, delimiter=',')

        start_timestamp = 0

        for index in range(1, len(my_data)):
            row = my_data[index]

            if start_timestamp == 0:
                start_timestamp = row[0]

            if row[1] == 100:
                e_time = row[0] - start_timestamp
                execution_times.append(e_time)
                break
    
    return execution_times

def get_step_dataset_delay(path):
    files = [f for f in glob.glob(path + "/*.csv", recursive=True)]

    delays = []

    for f in files:
        my_data = genfromtxt(f, delimiter=',')

        start_timestamp = 0

        for index in range(1, len(my_data)):
            row = my_data[index]

            if start_timestamp == 0:
                start_timestamp = row[0]

            if row[1] != 0:
                e_time = row[0] - start_timestamp
                delays.append(e_time)
                break
    
    return delays

def avg(dataset):
    value = 0
    length = len(dataset)

    if length == 0:
        return value

    value = sum(dataset) / length

    return value

def get_avg_delay(data_steps, step=None):
    delays = []

    if step is not None:
        dataset = data_steps[step]
        for item in dataset:
            print(item)
    else:
        for step in range(0, length(data_steps)):
            dataset = data_steps[step]
            for execution in dataset:
                pass

    return delays

if __name__ == "__main__":
    data327 = [get_step_dataset(f"{EXP_DIR327}/step{i + 1}") for i in range(0, LARGER_STEP)]
    avg_327 = [avg(x) for x in data327]

    data800 = [get_step_dataset(f"{EXP_DIR800}/step{i + 1}") for i in range(0, LARGER_STEP)]
    avg_800 = [avg(x) for x in data800]

    delays327 = [get_step_dataset_delay(f"{EXP_DIR327}/step{i + 1}") for i in range(0, LARGER_STEP)]
    delays800 = [get_step_dataset_delay(f"{EXP_DIR800}/step{i + 1}") for i in range(0, LARGER_STEP)]

    #Dealing with the outliers within a tolence of 5%:
    for index in range(len(data327)):
        data327[index] = scipy.stats.mstats.winsorize(data327[index], limits=[0.05, 0.05])

    for index in range(len(data800)):
        data800[index] = scipy.stats.mstats.winsorize(data800[index], limits=[0.05, 0.05])

    #"""

    # Choose the height of the blue bars
    bars_327 = [(data_simu_327[x] / avg_327[x]) * 100 for x in range(0, LARGER_STEP)]

    bars_800 = [(data_simu_800[x] / avg_800[x]) * 100  for x in range(0, LARGER_STEP)]
    #bars_simu = [data_simu_327[index] ifor index in range(LARGER_STEP)]

    # Choose the height of the error bars (bars1)
    y_error_327 = [mean_confidence_interval(x, 0.95) for x in data327]
    y_error_800 = [mean_confidence_interval(x, 0.95) for x in data800]

    # The x position of bars
    r1 = np.arange(len(bars_327)) * 0.5
    r2 = [x + barWidth for x in r1]
    
    # Create blue bars
    plt.bar(r1, bars_327, width=barWidth, color='burlywood', edgecolor='black', capsize=7, label='Workload 327')
    plt.bar(r2, bars_800, width=barWidth, color='teal', edgecolor='black', capsize=7, label='Workload 800')

    # general layout
    x_label = [f"Step {x + 1}" for x in range(len(data327))]
    x_ticks = [r * 0.5 + barWidth/2 for r in range(len(bars_327))]

    plt.xticks(x_ticks, x_label)

    plt.ylabel("Simulation Time / Real Time")
    plt.legend()
    plt.title(f"Simulation Time as a ratio of the Real Time")
    plt.grid()
    # Show graphic
    plt.show()
