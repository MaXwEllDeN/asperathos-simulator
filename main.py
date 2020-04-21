import simpy

from modules.aspqueue import Queue
from modules.workermanager import WorkerManager
from modules.pidcontroller import PIDController
from modules.aspplots import generate_plots

import argparse

SIMULATION_TIME = 150

WORKLOADS = ["https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt",

"https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt"
]

# WORKLOADS
# 0: 327 items
# 1: 800 items

KP, KI, KD = 0.1, 0.1, 0

CONTROLLER_ACTUATION_TIME = 3

MONITOR_CHECK_INTERVAL = 2

MONITOR_DATA = []

def publishMonitorData(model):
    MONITOR_DATA.append(model)

def getMonitorData():
    return MONITOR_DATA

def monitor(env, queue, wmanager):
    desired_time = 15 # seconds

    # Process variable: Jp/s
    starting_time = env.now

    jpps = 0 # Job progress per second

    decreasing = False

    setpoint = 100 / desired_time # wanted_jpps

    last_progress = 0
    execution_time = 0
  
    while True:
        progress = queue.get_progress()
        jpps_now = (progress - last_progress) / MONITOR_CHECK_INTERVAL
        
        if jpps_now < jpps:
            decreasing = True
        else:
            decreasing = False
        
        if (jpps_now != 0) or (jpps_now != 0 and decreasing):
            jpps = jpps_now

        last_progress = progress
   
        replicas = wmanager.get_replicas_count()
        execution_time = env.now - starting_time

        error = setpoint - jpps

        print("Progress: {}% with {} replica(s).".format(round(progress, 2), replicas))
        print("Job Progress per seconds: {}".format(round(jpps, 2)))
        print("Execution Time: {}".format(round(execution_time, 2)))
        print("-----------")

        model = {
            "time": execution_time,
            "job_progress": progress,
            "jpps": jpps,
            "replicas": replicas,
            "error": error,
            "setpoint": setpoint
        }

        publishMonitorData(model)

        if queue.get_progress() == 100:
            break

        yield env.timeout(MONITOR_CHECK_INTERVAL)

    print("Execution time: {0:.2f} seconds.".format(execution_time))

def pid_controller(env, wmanager):
    # dt Must be the rating at which the error is updated
    controller = PIDController(KP, KI, KD, MONITOR_CHECK_INTERVAL)

    data = getMonitorData()[-1]

    while data["job_progress"] < 100:
        data = getMonitorData()[-1]
        replicas = data["replicas"]
        control_action = controller.work(data["error"])

        if replicas < round(control_action, 0):
            increasing = int(round(control_action, 0) - replicas)

            for _ in range(0, increasing):
                wmanager.launch_replica()

            print("{} new replicas launched.".format(increasing))
        elif replicas > round(control_action, 0):
            decreasing = int(replicas - round(control_action, 0))
            decreasing = min(decreasing, replicas)

            for _ in range(0, decreasing):
                wmanager.remove_replica()

            print("Deleting {} replicas...".format(decreasing))

        yield env.timeout(CONTROLLER_ACTUATION_TIME)

def default_controller(env, wmanager, step=1):
    data = getMonitorData()[-1]

    for _ in range(0, step):
        wmanager.launch_replica()

    while data["job_progress"] < 100:
        data = getMonitorData()[-1]

        yield env.timeout(CONTROLLER_ACTUATION_TIME)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("step", help="number of worker replicas that should be deployed", type=int)
    parser.add_argument("workload", type=int)
    args = parser.parse_args()

    env = simpy.Environment()
    queue = Queue(WORKLOADS[args.workload])

    wmanager = WorkerManager(env, queue)
    env.process(monitor(env, queue, wmanager))

    env.process(default_controller(env, wmanager, args.step))

    try:
        env.run(until=SIMULATION_TIME)
    except KeyboardInterrupt:
        print("Bye bye")

    generate_plots(MONITOR_DATA)

    """

    if (args.hit_rate <= 0 or args.hit_rate > 100):
        print("hit_rate must be between 1 and 100 percent")
        exit()

    print("Vamo dale")

    try:

        for _ in range(0, args.replicas):
            wmanager.launch_replica()

        simulation_data = monitor(queue, wmanager)

        generate_plots(simulation_data)
    except KeyboardInterrupt:
        print("Bye bye")
    """
