MONITOR_CHECK_INTERVAL = 2

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
        # setpoint = expected_time
        # error = setpoint - process_variable

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

def stream_monitor(queue_time, env, queue, wmanager, persistence):
    debug_msg("Stream monitor yet to be implemented.")

    starting_time = 0

    last_total_items = 0
    last_completed = 0

    while wmanager.is_running():
        progress = queue.get_progress()
        replicas = wmanager.get_replicas_count()
        execution_time = env.now - starting_time
        
        completed_items = queue.get_completed_counter()
        real_output_flux = float(completed_items - last_completed) / MONITOR_CHECK_INTERVAL
        last_completed = completed_items

        total_items = queue.get_total_items_counter()
        input_flux = float(total_items - last_total_items) / MONITOR_CHECK_INTERVAL
        last_total_items = total_items

        main_q_size = queue.get_waiting_items_counter()

        expected_output_flux = replicas/queue_time
        #error1 = expected_output_flux - input_flux        
        error = real_output_flux - input_flux

        model = {
            "time": execution_time,
            "job_progress": progress,
            "replicas": replicas,
            "error": error,
            "setpoint": real_output_flux,
            "input_flux": input_flux,
            "output_flux": real_output_flux
        }

        debug_msg("========================")
        #debug_msg("Error option: %s" % error_option)
        #debug_msg("Correction term: %s" % corrector_term)
        #debug_msg("Error: %s" % error)
        debug_msg("Replicas: %s" % replicas)
        debug_msg("Inserted items : %i" % total_items)
        debug_msg("Queue size: %s" % main_q_size)
        #debug_msg("Pods Processins: %s" % num_processing_jobs)
        debug_msg("Items Completed: %i" % completed_items)
        #self.LOG.log("Lease expired: %i" % lease_expired)
        debug_msg("Input Flux : %s" % input_flux)
        debug_msg("Real output Flux : %s" % real_output_flux)
        #self.LOG.log("Expected output Flux : %s" % expected_output_flux)
        #self.LOG.log("Collect period : %s" % str(self.collect_period))
        debug_msg("Execution Time: {} seconds".format(round(execution_time, 2)))
        debug_msg("========================")

        persistence.publish(model)
        yield env.timeout(MONITOR_CHECK_INTERVAL)
