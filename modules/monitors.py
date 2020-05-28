MONITOR_CHECK_INTERVAL = 2
CONTROLLER_ACTUATION_TIME = 2

def debug_msg(msg):
    print(f"[MONITOR]: {msg}")

def batch_monitor(expected_time, env, queue, wmanager, persistence):
    # Process variable: Jp/s
    starting_time = env.now

    execution_time = 0
  
    while wmanager.is_running():
        progress = queue.get_progress()
 
        replicas = wmanager.get_replicas_count()
        execution_time = env.now - starting_time

        # Conventional way:
        #setpoint = expected_time
        #error = setpoint - process_variable

        # Asperathos way:
        setpoint = execution_time / expected_time
        ref_value = setpoint
        error = (progress/100) - ref_value

        debug_msg("Progress: {}% with {} replica(s)".format(round(progress, 2), replicas))
        debug_msg("Execution Time: {} seconds".format(round(execution_time, 2)))
        debug_msg("Setpoint: {}".format(round(setpoint, 2)))
        debug_msg("-----------")

        model = {
            "time": execution_time,
            "job_progress": progress,
            "replicas": replicas,
            "error": error,
            "setpoint": setpoint
        }

        persistence.publish(model)

        if queue.get_progress() == 100:
            wmanager.stop()

        yield env.timeout(MONITOR_CHECK_INTERVAL)

    debug_msg("Job completed with {0:.2f} seconds.".format(execution_time))

def stream_monitor(env, queue, wmanager, persistence):
    debug_msg("Stream monitor yet to be implemented.")

    while wmanager.is_running():
        debug_msg("I will make a cup of coffee...")

        yield env.timeout(MONITOR_CHECK_INTERVAL)
