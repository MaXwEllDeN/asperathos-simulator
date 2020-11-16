#batch_validation.py
import glob
import scipy.stats
import numpy as np
import matplotlib.pyplot as plt

SIM_EXECUTION_TIME = {
    "327": [72, 40, 28, 24, 22, 20, 18, 18, 18, 18, 18, 18],
    "800": [166, 86, 60, 48, 40, 36, 32, 30, 28, 26, 26, 26]
}

WORKLOADS = [
    (327, "/home/maxwell/workspace/lsd/repos/asperathos-simulator/experiments/batch/wl327"),
    (800, "/home/maxwell/workspace/lsd/repos/asperathos-simulator/experiments/batch/wl800")
]

def get_step_dataset(path):
    files = [f for f in glob.glob(path + "/*.csv", recursive=True)]

    execution_times = []

    for f in files:
        my_data = np.genfromtxt(f, delimiter=',')

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

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return h

if __name__ == "__main__":
    barWidth = 0.1

    for workload in WORKLOADS:
        fig = plt.figure()

        bars_sim = SIM_EXECUTION_TIME[str(workload[0])]
        exp_data = [get_step_dataset(f"{workload[1]}/step{x}") for x in range(1, len(bars_sim) + 1)]

        bars_real = [np.average(step_data) for step_data in exp_data]
        yer = [mean_confidence_interval(step_data) for step_data in exp_data]

        r1 = np.arange(len(bars_real)) * 0.7
        r2 = [x + barWidth for x in r1]

        plt.bar(r1, bars_real, width=barWidth, color='blue', edgecolor='black', yerr=yer, capsize=10, label="Real")
        plt.bar(r2, bars_sim, width=barWidth, color='cyan', edgecolor='black', label="Simulator")

        xticks = [f"Step {x}" for x in range(1, len(bars_real) + 1)]
        plt.xticks([r + barWidth/2 for r in r1], xticks, fontsize=13)
        plt.yticks(fontsize=13)
        plt.ylabel("Execution time (s)", fontsize=14)
        plt.title(f"Average execution time for a {workload[0]} items workload", fontsize=17)
        plt.legend(fontsize=14)
        plt.grid()
        plt.show()