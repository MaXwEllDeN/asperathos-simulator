from aspqueue import Queue
from pidcontroller import PIDController
from workermanager import WorkerManager
from aspplots import generate_plots

from numpy import absolute
import threading
import argparse
import requests
import time

URL_WORKLOAD_327 = "https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt"

URL_WORKLOAD_800 = "https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt"

KP, KI, KD = 3, 1, 0.5

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

def monitor(queue, wmanager):
    now = 0
    starting_time = now
    #starting_time = time.time()

    #Process variable: Jp/s

    simulation_data = []

    print("Vamo dale")
    jpps = 0 # Job progress per second
    last_progress = 0
    last_completed = 0
    interval = 2

    target_time = 15.68
    execution_time = 0

    jpps_array = []
    setpoint_array = []
    setpoint = 0
   
    while True:
        progress = queue.get_progress()
        jpps = (progress - last_progress) / interval
        last_progress = progress        

        jpps_array.append(jpps)
        avg_jpps = sum(jpps_array) / len(jpps_array)
    
        completed = queue.get_completed_counter()        
        jps = (completed - last_completed) / interval
        last_completed = completed

        replicas = wmanager.get_replicas_count()

        print("Progress: {}% with {} replica(s).".format(round(progress, 2), replicas))
        print("Avg JP/s: {}".format(round(avg_jpps, 2)))
        print("Execution Time JP/s: {}".format(round(execution_time, 2)))

        if execution_time > target_time:
            print("We are late.")
        else:            
            setpoint = (100 - progress) / (target_time - execution_time)

            if (absolute(setpoint) > 20):
                setpoint = 0

            setpoint_array.append(setpoint)
            avg_setpoint = sum(setpoint_array) / len(setpoint_array)

            print("Avg Setpoint JP/s: {}".format(round(setpoint, 2)))

        print("--------------------")

        execution_time = now - starting_time
        model = {
            "time": execution_time,
            "job_progress": progress,
            "avg_jpps": avg_jpps,            
            "completed": completed,         
            "setpoint": setpoint,
            "avg_setpoint": 0
        }

        simulation_data.append(model)

        now += interval

        if queue.get_progress() == 100:
            break

        time.sleep(interval)

    print("Execution time: {0:.2f} seconds.".format(execution_time))
    
    return simulation_data

if __name__ == "__main__":
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
        queue = Queue(URL_WORKLOAD_327)
        wmanager = WorkerManager(queue, hit_rate=args.hit_rate)

        for _ in range(0, args.replicas):
            wmanager.launch_replica()

        simulation_data = monitor(queue, wmanager)

        generate_plots(simulation_data)
    except KeyboardInterrupt:
        print("Bye bye")

# Execution time: 161.22 seconds.