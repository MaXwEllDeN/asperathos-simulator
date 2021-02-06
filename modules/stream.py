from math import floor
def populate_queue(env, queue, wmanager):
    '''
        Populate the queue with items over time
        
        :param: env
            simpy simulation environment
        :param: queue
            queue to be populated
        :param: wmanager
            worker manager that handles the execution jobs

        :returns: nothing
    '''

    item_count = 0
    DURATION = 5 * 60
    LOOPS = 1
    workload = [2, 4, 2, 4]

    cycles_per_loop = len(workload) 
    total_cycles = cycles_per_loop * LOOPS 
    cycle_duration = DURATION / total_cycles 

    for loop in range(LOOPS):
        print(" Loop " + str(loop))

        for cycle in range(cycles_per_loop):
            print("  Cycle " + str(cycle))
            
            cycle_value = workload[cycle] 
            cycle_items = cycle_value * cycle_duration 
            
            print("     Items per second: ", cycle_value)
            print("     Total items in cycle: ", cycle_items)

            if (cycle_items) != 0 :
                cycle_wait_time = cycle_duration/cycle_items
                print("     Wait time: ", cycle_wait_time)

                for i in range(floor(cycle_items)):
                    item_count += 1

                    queue.push_item("how you like that")
                    yield env.timeout(cycle_wait_time)
            else :
                # if the cycle is 0, we only wait for the entire duration
                print("     Wait time: ",cycle_duration)
                yield env.timeout(cycle_duration)

    """            
    while wmanager.is_running():
        queue.push_item("how you like it")
        yield env.timeout(1 / ITEMS_PER_SECOND)
    """