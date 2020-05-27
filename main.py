import simpy
import argparse

from modules.aspqueue import Queue
from modules.workermanager import WorkerManager
from modules.aspplots import generate_plots

from modules.utils import PersistenceManager

SIMULATION_TIME = 3600
MAX_REPLICAS = 10
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
    parser_b.add_argument('queue_time', choices='XYZ', help='baz help')

    parser.add_argument('-c', choices=["default", "pid"], help='Controller type', default="default")

    # parse argument lists
    args = parser.parse_args()

    APP_MODE = None

    if args.expected_time:
        APP_MODE = "batch"
    elif args.queue_time:
        APP_MODE = "stream"

    env = simpy.Environment()
    queue = Queue(WORKLOADS[str(args.workload)])

    wmanager = WorkerManager(env, queue, APP_MODE, max_replicas=MAX_REPLICAS, min_replicas=MIN_REPLICAS)
    pmanager = PersistenceManager()

    # loading monitor
    if APP_MODE == "batch":
        from modules.monitors import batch_monitor as monitor
        env.process(monitor(args.expected_time, env, queue, wmanager, pmanager))
    elif APP_MODE == "stream":
        from modules.monitors import stream_monitor as monitor
    
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
        generate_plots(f"Simulation for expected time = {args.expected_time} seconds", pmanager.getData())
    elif APP_MODE == "stream":
        pass
