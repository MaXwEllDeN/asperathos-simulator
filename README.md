
# Asperathos Simulator

## Batch

- On `main.py` you can add more workload choices by including them on `WORKLOADS` list.
- On the `WorkerManager` module, the `batch_worker` function mimics the real execution of a batch application.

### Execution
`python3 main.py [-c {default,pid}] batch <expected_time> <workload>`

* `expected_time`: total time expected for the job progress to be completed.
* `workload`: initial workload to be loaded to the queue, chosen from `WORKLOADS` list.

## Stream
For streaming applications, you must implement a function to populate the queue on the `stream` module.

### Execution
`python3 main.py [-c {default,pid}] stream <queue_time>`
* `queue_time`: the maximum time expected that an item ideally should spend on the queue before completion. 

## Modules

### Controllers
It contains implementations for each specific controller.

Available controllers:
* **PID**: based on the control theory about controllers, choose the best number of replicas for reference tracking.
* **Default**: raise or lower the number of replicas depending on an error threshold.

### Monitors
It provides monitor functions to publish information about the running job. It's where the error is specified.
 
### WorkerManager
It handles replicas and worker functions.

### Visualizer
It provides a way to visualize the simulation data. At current moment the user is only able to visualize execution data after the simulation has been completed.
