import simpy
import requests
import argparse

from modules.aspqueue import Queue
from modules.workermanager import WorkerManager
import modules.visualizer as visualizer

from modules.utils import PersistenceManager

SIMULATION_TIME = 60
MAX_REPLICAS = 20
MIN_REPLICAS = 1

WORKLOADS = {
    "327": "https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt",

    "800": "https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt"
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="subcommands", help='simulator modes')

    # create the parser for the "batch" command
    parser_a = subparsers.add_parser('batch', help='batch application')
    parser_a.add_argument('expected_time', type=int, help='expected time in seconds')
    parser_a.add_argument('workload', type=int, help='workload', choices=[327, 800])

    # create the parser for the "stream" command
    parser_b = subparsers.add_parser("stream", help='stream application')
    parser_b.add_argument('queue_time', type=int, help='desired queue time')

    parser.add_argument('-c', choices=["default", "pid"], help='Controller type', default="default")

    # parse argument lists
    args = parser.parse_args()

    APP_MODE = None

    if "expected_time" in args:
        APP_MODE = "batch"
    elif "queue_time" in args:
        APP_MODE = "stream"

    env = simpy.Environment()
    pmanager = PersistenceManager()
    wmanager = None
    queue = None

    if APP_MODE == "batch":
        # loading workload from URL
        items_from_url = []

        req = requests.get(WORKLOADS[str(args.workload)])

        for url in req.text.split("\n"):
            items_from_url.append(url)

        queue = Queue(items_from_url)
        
        wmanager = WorkerManager(env, queue, "batch", max_replicas=MAX_REPLICAS, min_replicas=MIN_REPLICAS)

        # loading monitor
        from modules.monitors import batch_monitor as monitor
        env.process(monitor(args.expected_time, env, queue, wmanager, pmanager))

    elif APP_MODE == "stream":
        from modules.monitors import stream_monitor as monitor
        from modules.stream import populate_queue

        # init empty queue
        queue = Queue()
        
        wmanager = WorkerManager(env, queue, "stream", max_replicas=MAX_REPLICAS, min_replicas=MIN_REPLICAS)
        env.process(monitor(args.queue_time, env, queue, wmanager, pmanager))
        env.process(populate_queue(env, queue, wmanager))
   
    # loading controller
    if args.c == "default":
        from modules.controllers import default_controller as controller
    elif args.c == "pid":
        from modules.controllers import pid_controller as controller

    env.process(controller(env, wmanager, pmanager))

    try:
        env.run(until=SIMULATION_TIME)
    except KeyboardInterrupt:
        print("Bye bye")

    if APP_MODE == "batch":
        print("Generating plots...")
        visualizer.batch(f"Simulation for expected time = {args.expected_time} seconds", pmanager.getData())
    elif APP_MODE == "stream":
        visualizer.stream(f"Simulation for queue time = {args.queue_time} seconds", pmanager.getData())
