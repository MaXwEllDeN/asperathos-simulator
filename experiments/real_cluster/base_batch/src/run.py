#!/usr/bin/env python
import os
import ssl
import sys
import time

import rediswq

# After LEASE_SECS, an unfinished work item will
# return to the main queue (work to be done).
LEASE_SECS = 10

# DEV-ONLY: bypass redis and process a static item.
# this is for testing purposes.
DEV_MODE = os.environ.get('APP_DEV_MODE', False)
DEV_ITEM = os.environ.get('APP_DEV_ITEM')

def process_client(data, q):
    """This is where the processing functin should be"""
    time.sleep(0.2)
    q.publish_result(data)

    """
    with open("/output/%s"%data, "w+") as output:
        output.write(result)
    """

    return True


def run():

    # for dev purposes only: bypass redis and process static item.
    if DEV_MODE and DEV_ITEM is not None:
        print('INFO:Running in dev-mode with: %s' % DEV_ITEM)
        print(process_client(DEV_ITEM, None))
        return True

    # get Redis address from environemnt.
    # defaults to 'redis:6379' using the queue 'job'.
    redis_host = os.environ.get('REDIS_HOST')
    redis_port = os.environ.get('REDIS_PORT', 6379)
    redis_queue = os.environ.get('REDIS_QUEUE', 'job')

    # falling back to 'redis' is more useful than the
    # default 'localhost', especially in k8s clusters.
    if redis_host is None:
        print('WARNING:You did not provide a Redis host. ' +
              'Falling back to "redis".')
        redis_host = 'redis'

    print("INFO:Trying to reach redis running at %s:%s. Using queue %s." % (redis_host, redis_port, redis_queue))
    queue = rediswq.RedisWQ(name=redis_queue, host=redis_host, port=redis_port)
    print("INFO:Connection established")
    print("INFO:Worker with sessionID: " + queue.sessionID())

    while not queue.empty():
        print("INFO:Consulting work queue for the next item.")
        object_url = queue.lease(lease_secs=LEASE_SECS, block=True, timeout=2)

        item_start = time.time()

        if object_url is not None:
            print("INFO:Processing item... " + object_url.decode("utf=8"))
            if process_client(object_url, queue):
                queue.complete(object_url)

                time_spent = time.time() - item_start

                print("INFO:Item completed. Results posted. '{}' seconds to process item.".format(time_spent))
        else:
            queue.check_expired_leases()
            print("INFO:Waiting for work...")

if __name__ == '__main__':
    print('INFO:Application started!')
    run()
