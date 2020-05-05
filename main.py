import simpy

from modules.aspqueue import Queue
from modules.workermanager import WorkerManager
from modules.pidcontroller import PIDController
from modules.aspplots import generate_plots

import argparse

SIMULATION_TIME = 200

WORKLOADS = ["https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt",

"https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt"
]

# WORKLOADS
# 0: 327 items
# 1: 800 items

CONTROLLER_ACTUATION_TIME = 2
MONITOR_CHECK_INTERVAL = 2

MONITOR_DATA = []

def publishMonitorData(model):
    MONITOR_DATA.append(model)

def getMonitorData():
    return MONITOR_DATA

def monitor(expected_time, env, queue, wmanager):
    # Process variable: Jp/s
    starting_time = env.now

    jpps = 0 # Job progress per second

    decreasing = False

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

        # Conventional way:
        #setpoint = expected_time
        #error = setpoint - jpps

        # Asperathos way:
        setpoint = execution_time / expected_time
        ref_value = setpoint
        error = (progress/100) - ref_value

        print("Progress: {}% with {} replica(s).".format(round(progress, 2), replicas))
        print("Job Progress per seconds: {}".format(round(jpps, 2)))
        print("Execution Time: {}".format(round(execution_time, 2)))
        print("Setpoint: {}".format(round(setpoint, 2)))
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
    KP, KI, KD = 0.1, 0.1, 0
    controller = PIDController(KP, KI, KD, MONITOR_CHECK_INTERVAL)

    data = getMonitorData()[-1]

    while data["job_progress"] < 100:
        data = getMonitorData()[-1]
        replicas = data["replicas"]
        control_action = int(controller.work(data["error"]))

        wmanager.adjust_resources(control_action)

        yield env.timeout(CONTROLLER_ACTUATION_TIME)

def default_controller(env, wmanager):
    DELAY_TO_CHANGE_REPLICAS = 5

    ACTUATION_SIZE = 2
    MAX_REPLICAS = 10
    TRIGGER_UP = 0
    TRIGGER_DOWN = 0

    wmanager.adjust_resources(1)
    wmanager.set_max_replicas(MAX_REPLICAS)

    yield env.timeout(DELAY_TO_CHANGE_REPLICAS)

    data = getMonitorData()[-1]

    while data["job_progress"] < 100:
        data = getMonitorData()[-1]

        if data["error"] > 0 and data["error"] >= TRIGGER_DOWN:
            wmanager.adjust_resources(data["replicas"] - ACTUATION_SIZE)
        elif data["error"] < 0 and abs(data["error"]) >= TRIGGER_UP:
            wmanager.adjust_resources(data["replicas"] + ACTUATION_SIZE)

        yield env.timeout(CONTROLLER_ACTUATION_TIME)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("expected_time", help="Expected execution time.", type=int)    
    parser.add_argument("workload", type=int)
    args = parser.parse_args()

    env = simpy.Environment()
    queue = Queue(WORKLOADS[args.workload])

    wmanager = WorkerManager(env, queue)
    env.process(monitor(args.expected_time, env, queue, wmanager))
    env.process(default_controller(env, wmanager))

    try:
        env.run(until=SIMULATION_TIME)
    except KeyboardInterrupt:
        print("Bye bye")

    generate_plots(f"Simulation for expected time = {args.expected_time} seconds", MONITOR_DATA)
