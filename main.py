import simpy
from aspqueue import Queue
from workermanager import WorkerManager
#from pidcontroller import PIDController
#from aspplots import generate_plots

#from numpy import absolute
#import threading
import argparse
#import requests
#import time

URL_WORKLOAD_327 = "https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt"

URL_WORKLOAD_800 = "https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt"

KP, KI, KD = 3, 1, 0.5

def monitor(env, queue, wmanager):
    # Process variable: Jp/s    
    starting_time = env.now
    simulation_data = []

    jpps = 0 # Job progress per second

    last_progress = 0
    last_completed = 0
    CHECK_INTERVAL = 2

    execution_time = 0
  
    while True:
        progress = queue.get_progress()
        jpps = (progress - last_progress) / CHECK_INTERVAL
        last_progress = progress
   
        replicas = wmanager.get_replicas_count()
        execution_time = env.now - starting_time

        print("Progress: {}% with {} replica(s).".format(round(progress, 2), replicas))
        print("Execution Time JP/s: {}".format(round(execution_time, 2)))
        print("-----------")

        model = {
            "time": execution_time,
            "job_progress": progress,
            "replicas": replicas
        }

        simulation_data.append(model)

        if queue.get_progress() == 100:
            break

        yield env.timeout(CHECK_INTERVAL)

    print("Execution time: {0:.2f} seconds.".format(execution_time))

def controller(env, queue, wmanager):
    ACTUATION_TIME = 3

    wmanager.launch_replica()
    wmanager.launch_replica()
    while True:
        yield env.timeout(ACTUATION_TIME)

    """ Controller
    if replicas < round(control_action, 0):
        increasing = int(round(control_action, 0) - replicas)

        for _ in range(0, increasing):
            wmanager.launch_replica()

        print("{} new replicas launched.".format(increasing))
    elif replicas > round(control_action, 0):
        decreasing = int(replicas - round(control_action, 0))

        for _ in range(0, decreasing):
            wmanager.remove_replica()

        print("Deleting {} replicas...".format(decreasing))
    """
    pass

def main():
    SIMULATION_TIME = 150

    env = simpy.Environment()
    queue = Queue(URL_WORKLOAD_327)

    wmanager = WorkerManager(env, queue)
    env.process(monitor(env, queue, wmanager))
    env.process(controller(env, queue, wmanager))

    try:
        env.run(until=SIMULATION_TIME)
    except KeyboardInterrupt:
        print("Bye bye")

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