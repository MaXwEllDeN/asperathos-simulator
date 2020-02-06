from random import randrange
from aspqueue import Queue

import threading
import argparse
import requests
import time

URL_WORKLOAD_327 = "https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt"

URL_WORKLOAD_800 = "https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt"

def process_item(item, hit_rate):    
    url = item.content

    try:
        req = requests.get(url)

        if randrange(0, 100) <= hit_rate:
            return True
        else:
            return False
    except:
        return False

def worker(queue, hit_rate):
    try:    
        while (queue.get_progress() < 100):
            item = queue.get_item_to_process()

            if item == None:
                continue

            status = process_item(item, hit_rate)
                    
            if status == True:
                queue.complete_item(item)
            else:
                queue.rewind_item(item)

        return True
    except KeyboardInterrupt:
        return False

def monitor(queue, starting_time):
    print("Vamo dale")
    jpps = 0 # Job progress per second
    last_progress = 0
    interval = 0.1

    list_jpps = []
    avg_jpps = 0
    estimated_time = 0

    while (queue.get_progress() < 100):
        progress = queue.get_progress()       
        jpps = (progress - last_progress) / interval
        list_jpps.append(jpps)
        last_progress = progress
        
        avg_jpps = sum(list_jpps) / len(list_jpps)

        thread_count = threading.active_count() - 1
        print("Progress: {}% with {} replica(s).".format(round(progress, 2), thread_count))
        print("Average JP/s: {}".format(round(avg_jpps, 2)))

        if (avg_jpps != 0):
            estimated_time = 100/avg_jpps            
            print("Estimated time: {} seconds".format(round(estimated_time, 2)))
        else:
            print("Estimated time: infinite.")

        print("--------------------")
        time.sleep(interval)

    execution_time = time.time() - starting_time

    print("Execution time: {0:.2f} seconds.".format(execution_time))    
    print("Estimated time: {} seconds, deviation: {} seconds.".format(
        round(estimated_time, 2), round(estimated_time - execution_time, 2)))
    
    return True
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("replicas", help="number of worker replicas that should be deployed", type=int)
    parser.add_argument("hit_rate", help="probability of successfully processing an item", type=int)
    args = parser.parse_args()

    if (args.hit_rate <= 0 or args.hit_rate > 100):
        print("hit_hate shall lay between 1 and 100 percent")
        exit()

    starting_time = time.time()
    try:
        queue = Queue(URL_WORKLOAD_800)
        workers = []

        for i in range(0, args.replicas):
            w = threading.Thread(target=worker, args=(queue, args.hit_rate))
            workers.append(w)
            w.start()

        monitor(queue, starting_time)

    except KeyboardInterrupt:
        print("Bye bye")
