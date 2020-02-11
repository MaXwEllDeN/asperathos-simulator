from aspqueue import Queue
from pidcontroller import PIDController
from workermanager import WorkerManager
from aspplots import generate_plots

import threading
import argparse
import requests
import time

URL_WORKLOAD_327 = "https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt"

URL_WORKLOAD_800 = "https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt"

KP, KI, KD = 3, 1, 0.5

def monitor(queue, wmanager):
    starting_time = time.time()

    simulation_data = []

    print("Vamo dale")
    jpps = 0 # Job progress per second
    last_progress = 0
    interval = 1

    list_jpps = []
    avg_jpps = 0
    estimated_time = 0
    execution_time = 0
   
    while (queue.get_progress() < 100):
        progress = queue.get_progress()

        jpps = (progress - last_progress) / interval
        last_progress = progress

        list_jpps.append(jpps)
      
        avg_jpps = sum(list_jpps) / len(list_jpps)

        replicas = wmanager.get_replicas_count()

        print("Progress: {}% with {} replica(s).".format(round(progress, 2), replicas))
        print("Average JP/s: {}".format(round(avg_jpps, 2)))

        if (avg_jpps != 0):
            estimated_time = 100 / avg_jpps            
            print("Estimated time: {} seconds".format(round(estimated_time, 2)))
        else:
            print("Estimated time: infinite.")

        """
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

        print("--------------------")

        execution_time = time.time() - starting_time
        model = {
            "time": execution_time,
            "job_progress": progress,
            "avg_jpps": avg_jpps,
            "replicas": replicas,
        }

        simulation_data.append(model)


        time.sleep(interval)


    print("Execution time: {0:.2f} seconds.".format(execution_time))    
    print("Estimated time: {} seconds, deviation: {} seconds.".format(
        round(estimated_time, 2), round(estimated_time - execution_time, 2)))
    
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
        queue = Queue(URL_WORKLOAD_800)
        wmanager = WorkerManager(queue, hit_rate=args.hit_rate)

        for _ in range(0, args.replicas):
            wmanager.launch_replica()

        simulation_data = monitor(queue, wmanager)

        generate_plots(simulation_data)
    except KeyboardInterrupt:
        print("Bye bye")



