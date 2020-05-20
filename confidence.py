import glob
import numpy as np
import scipy.stats
from numpy import genfromtxt
import matplotlib.pyplot as plt

LARGER_STEP = 12
WORKLOAD = 327
EXP_DIR = f"/home/maxwell/workspace/lsd/asperathos-simulator/experiments/real_cluster/output/wl{WORKLOAD}"

# Execution times on simulator
data_simu_800 = [148, 80, 54, 40, 32, 28, 24, 20, 18, 16, 16, 14]
data_simu_327 = [66, 34, 24, 18, 16, 14, 12, 10, 10, 12, 12, 12]

data_simu = []

if WORKLOAD == 327:
    data_simu = data_simu_327
elif WORKLOAD == 800:
    data_simu_800

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

def avg(dataset):
    value = 0
    length = len(dataset)

    if length == 0:
        return value

    value = sum(dataset) / length

    return value

if __name__ == "__main__":
    data = [get_step_dataset(f"{EXP_DIR}/step{i + 1}") for i in range(0, LARGER_STEP)]

    """
    #Dealing with the outliers within a tolence of 5%:
    for index in range(len(data)):
        data[index] = scipy.stats.mstats.winsorize(data[index], limits=[0.05, 0.05])
    """

    # Choose the height of the blue bars
    bars_exp = [avg(x) for x in data]

    bars_simu = [data_simu[index] for index in range(LARGER_STEP)]

    # Choose the height of the error bars (bars1)
    y_error = [mean_confidence_interval(x, 0.95) for x in data]

    # The x position of bars
    r1 = np.arange(len(bars_exp)) * 0.5
    r2 = [x + barWidth for x in r1]
    
    # Create blue bars
    plt.bar(r1, bars_exp, width=barWidth, color='blue', edgecolor='black', yerr=y_error, capsize=7, label='Asperathos')
    plt.bar(r2, bars_simu, width=barWidth, color='cyan', edgecolor='black', capsize=7, label='Simulator')

    # general layout
    x_label = [f"Step {x + 1}" for x in range(len(data))]

    plt.xticks([r * 0.5 + barWidth/2 for r in range(len(bars_exp))], x_label)
    plt.ylabel("Execution time(s)")
    plt.legend()
    plt.title(f"Average execution time for a workload of {WORKLOAD} items")

    # Show graphic
    plt.show()