import time
import simpy
import requests
import threading

from random import randrange

class WorkerManager:
    PROCESSING_TIME = 0.2
    env = None
    queue = None
    hit_rate = None
    __workers = []

    def __init__(self, env, queue, hit_rate=100):
        self.env = env
        self.queue = queue
        self.hit_rate = hit_rate

    def launch_replica(self):
        w = self.env.process(self.worker())
        self.__workers.append(w)
        
        return w

    def remove_replica(self):
        try:
            if len(self.__workers) > 0:
                w = self.__workers.pop()
                w.interrupt("Finish")
        except Exception as e:
            pass


    def get_replicas_count(self):
        return len(self.__workers)

    def __process_item(self, item):
        url = item.content

        #req = requests.get(url)

        if randrange(0, 100) <= self.hit_rate:
            return True
        else:
            return False

    def worker(self):
        try:
            while self.queue.get_progress() < 100:            
                item = self.queue.get_item_to_process()

                if item == None:
                    continue

                status = self.__process_item(item)

                if status:
                    self.queue.complete_item(item)
                else:
                    self.queue.rewind_item(item)

                yield self.env.timeout(self.PROCESSING_TIME)
        except simpy.exceptions.Interrupt:
            pass
