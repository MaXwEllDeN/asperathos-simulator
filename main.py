from aspqueue import Queue
from pidcontroller import PIDController
from workermanager import WorkerManager

import threading
import argparse
import requests
import time

URL_WORKLOAD_327 = "https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt"

URL_WORKLOAD_800 = "https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt"

KP, KI, KD = 0.5, 0.5, 0.3

def monitor(queue, desired_time, wmanager):
    starting_time = time.time()

    print("Vamo dale")
    jpps = 0 # Job progress per second
    last_progress = 0
    interval = 1

    list_jpps = []
    avg_jpps = 0
    estimated_time = 0

    pid = PIDController(KP, KI, KD, interval)

    reference_jpps = 100 / desired_time

    while (queue.get_progress() < 100):
        progress = queue.get_progress()
        jpps = (progress - last_progress) / interval
        list_jpps.append(jpps)
        last_progress = progress
        
        avg_jpps = sum(list_jpps) / len(list_jpps)

        jpps_error = reference_jpps - avg_jpps
        control_action = pid.work(jpps_error)

        thread_count = threading.active_count() - 1
        print("Progress: {}% with {} replica(s).".format(round(progress, 2), thread_count))
        print("Average JP/s: {}".format(round(avg_jpps, 2)))

        if (avg_jpps != 0):
            estimated_time = 100/avg_jpps            
            print("Estimated time: {} seconds".format(round(estimated_time, 2)))
        else:
            print("Estimated time: infinite.")

        print("Error: {} jp/s".format(jpps_error))
        print("Control Action: {}".format(control_action))

        if thread_count < round(control_action, 0):
            increasing = int(round(control_action, 0) - thread_count)

            for _ in range(0, increasing):
                wmanager.launch_replica()

            print("{} new replicas launched.".format(increasing))
        elif thread_count > round(control_action, 0):
            decreasing = int(thread_count - round(control_action, 0))

            for _ in range(0, decreasing):
                wmanager.remove_replica()

            print("Deleting {} replicas...".format(decreasing))

        print("--------------------")
        time.sleep(interval)

    execution_time = time.time() - starting_time

    print("Execution time: {0:.2f} seconds.".format(execution_time))    
    print("Estimated time: {} seconds, deviation: {} seconds.".format(
        round(estimated_time, 2), round(estimated_time - execution_time, 2)))
    
    print("Deviation from desired time: {} seconds.".format(execution_time - desired_time))
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("execution_time", help="desired execution time", type=int)
    #parser.add_argument("replicas", help="number of worker replicas that should be deployed", type=int)
    parser.add_argument("hit_rate", help="probability of successfully processing an item", type=int)
    args = parser.parse_args()

    if (args.hit_rate <= 0 or args.hit_rate > 100):
        print("hit_rate shall lay between 1 and 100 percent")
        exit()

    print("Vamo dale")
    try:
        queue = Queue(URL_WORKLOAD_800)
        wmanager = WorkerManager(queue, hit_rate=args.hit_rate)
        monitor(queue, args.execution_time, wmanager)
    except KeyboardInterrupt:
        print("Bye bye")
