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
    max_replicas = 1
    min_replicas = 1
    __workers = []

    def __init__(self, env, queue, worker, max_replicas=1, min_replicas=1, hit_rate=100):
        self.env = env
        self.queue = queue
        self.hit_rate = hit_rate
        self.max_replicas = max_replicas
        self.min_replicas = min_replicas
        if worker.lower() == "batch":
            self.worker = self.batch_worker
        else:
            self.worker = self.stream_worker

    def launch_replicas(self, amount):
        for _ in range(0, amount):
            if self.get_replicas_count() >= self.max_replicas:
                break
            else:
                w = self.env.process(self.worker())
                self.__workers.append(w)

    def remove_replicas(self, amount):
        for _ in range(0, amount):
            if self.get_replicas_count() <= self.min_replicas:
                break
            else:
                if len(self.__workers) > 0:
                    w = self.__workers.pop()

                    if (w.is_alive):
                        w.interrupt("Finish")

    def set_max_replicas(self, replicas):
        self.max_replicas = replicas
        
    def set_min_replicas(self, replicas):
        self.min_replicas = replicas

    def get_replicas_count(self):
        return len(self.__workers)

    def adjust_resources(self, new_res):
        num_replicas = self.get_replicas_count()

        if num_replicas > new_res:
            self.remove_replicas(num_replicas - new_res)
        elif num_replicas < new_res:
            self.launch_replicas(new_res - num_replicas)


    def __process_item(self, item):
        url = item.content

        #req = requests.get(url)

        if randrange(0, 100) <= self.hit_rate:
            return True
        else:
            return False

    def batch_worker(self):
        item = None

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
            if item != None:
                self.queue.rewind_item(item)

    def stream_worker(self):
        item = None

        try:
            while True:            
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
            if item != None:
                self.queue.rewind_item(item)