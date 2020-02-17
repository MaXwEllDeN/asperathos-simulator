import time
import requests
import threading

from random import randrange

class WorkerManager:
    queue = None
    hit_rate = None
    __workers = []

    def __init__(self, queue, hit_rate=100):
        self.queue = queue
        self.hit_rate = hit_rate

    def launch_replica(self):
        w = WorkerThread(self.queue, self.hit_rate)
        self.__workers.append(w)

        w.start()

        return True

    def remove_replica(self):
        if len(self.__workers) > 0:
            w = self.__workers.pop()
            w.stop()
            return True

        return False

    def get_replicas_count(self):
        return len(self.__workers)

class WorkerThread(threading.Thread):
    queue = None
    hit_rate = 100

    def __init__(self, queue, hit_rate, *args, **kwargs):
        super(WorkerThread, self).__init__(*args, **kwargs) 
        self._stop = threading.Event() 
        self.queue = queue
        self.hit_rate = hit_rate
  
    def stop(self):
        self._stop.set() 
  
    def stopped(self): 
        return self._stop.isSet() 
  
    def __process_item(self, item):
        url = item.content

        #req = requests.get(url)
        time.sleep(0.2)

        if randrange(0, 100) <= self.hit_rate:
            return True
        else:
            return False

    def run(self):
        while not self.stopped() and self.queue.get_progress() < 100:            
            item = self.queue.get_item_to_process()
            if item == None:
                continue

            status = self.__process_item(item)
                    
            if status:
                self.queue.complete_item(item)
            else:
                self.queue.rewind_item(item)

        return True
