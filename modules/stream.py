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

    ITEMS_PER_SECOND = 3

    while wmanager.is_running():
        print(f"Adding item xDD... {env.now}")
        queue.push_item("how you like it")
        yield env.timeout(1 / ITEMS_PER_SECOND)