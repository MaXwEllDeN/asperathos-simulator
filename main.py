import simpy
from aspqueue import Queue
from workermanager import WorkerManager
from pidcontroller import PIDController
from aspplots import generate_plots

import argparse

URL_WORKLOAD_327 = "https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt"

URL_WORKLOAD_800 = "https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt"

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
    simulation_data = []

    jpps = 0 # Job progress per second

    last_progress = 0
    execution_time = 0

    setpoint = 100 / desired_time # wanted_jpps
  
    while True:
        progress = queue.get_progress()
        jpps = (progress - last_progress) / MONITOR_CHECK_INTERVAL
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

def main():
    SIMULATION_TIME = 150

    env = simpy.Environment()
    queue = Queue(URL_WORKLOAD_327)

    wmanager = WorkerManager(env, queue)
    env.process(monitor(env, queue, wmanager))
    env.process(pid_controller(env, wmanager))

    try:
        env.run(until=SIMULATION_TIME)
    except KeyboardInterrupt:
        print("Bye bye")

    generate_plots(MONITOR_DATA)

if __name__ == "__main__":
    main()
    """
    parser = argparse.ArgumentParser()
    #parser.add_argument("execution_time", help="desired execution time", type=int)
    parser.add_argument("replicas", help="number of worker replicas that should be deployed", type=int)
    parser.add_argument("hit_rate", help="probability of successfully processing an item", type=int)
    args = parser.parse_args()

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