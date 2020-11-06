#!/usr/bin/python
import json
import time
import requests
import argparse
import datetime
from aspplots import generate_plots

SUBMIT_ENDPOINT = "http://0.0.0.0:1500/submissions"
REPORT_ENDPOINT = "http://0.0.0.0:1500/submissions/{}/report"

WORKLOADS = [("https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt", 327),

("https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt", 800)
]

# WORKLOADS
# 0: 327 items
# 1: 800 items

parser = argparse.ArgumentParser()
parser.add_argument("expected_time", help="Expected execution time.", type=int)
parser.add_argument("workload", help="Workload.", type=int)
parser.add_argument("dir", help="Directory file.")
parser.add_argument("plot")

def strategy_scripted(job_json):
	CHECK_INTERVAL = 2
	MAX_REP = 10	
	STEP_INITIAL = 5
	STEP_AMPLITUDE = 1
	STEP_TIME = 15 # After x seconds, it will change the # of replicas	

	job_json["plugin_info"]["control_parameters"]["min_rep"] = STEP_INITIAL
	job_json["plugin_info"]["control_parameters"]["max_rep"] = MAX_REP	
	job_json["plugin_info"]["control_parameters"]["schedule_strategy"] = "scripted"
	job_json["plugin_info"]["control_parameters"]["check_interval"] = CHECK_INTERVAL

	job_json["plugin_info"]["control_parameters"]["heuristic_options"] = {}
	job_json["plugin_info"]["control_parameters"]["heuristic_options"]["rep_script"] = [STEP_INITIAL \
		for i in range(int((STEP_TIME - CHECK_INTERVAL)/CHECK_INTERVAL) - 1)]
	job_json["plugin_info"]["control_parameters"]["heuristic_options"]["rep_script"].append(STEP_AMPLITUDE)
    
	return job_json

def strategy_pid(job_json):
	CHECK_INTERVAL = 2
	MAX_REP = 10
	MIN_REP = 1	
	job_json["plugin_info"]["control_parameters"]["min_rep"] = MIN_REP
	job_json["plugin_info"]["control_parameters"]["max_rep"] = MAX_REP
	job_json["plugin_info"]["control_parameters"]["schedule_strategy"] = "pid"
	job_json["plugin_info"]["control_parameters"]["check_interval"] = CHECK_INTERVAL	

	job_json["plugin_info"]["control_parameters"]['heuristic_options'] = {
		'proportional_gain': 	0.03126,
		'integral_gain': 		0.03126,
		'derivative_gain': 		0.0
	}

	job_json["plugin_info"]["control_parameters"]['trigger_up'] = 0
	job_json["plugin_info"]["control_parameters"]['trigger_down'] = 0
	return job_json

def strategy_default(job_json):
	CHECK_INTERVAL = 2
	ACTUATION_SIZE = 1
	MAX_REP = 10
	MIN_REP = 1

	job_json["plugin_info"]["control_parameters"]["min_rep"] = MIN_REP
	job_json["plugin_info"]["control_parameters"]["max_rep"] = MAX_REP
	job_json["plugin_info"]["control_parameters"]["schedule_strategy"] = "default"
	job_json["plugin_info"]["control_parameters"]["check_interval"] = CHECK_INTERVAL

	job_json["plugin_info"]["control_parameters"]["actuation_size"] = ACTUATION_SIZE

	return job_json

def submit_job(expected_time, workload_url):
	IMG = "maxwellden/quickstart:demo"
	job_json = {'plugin': 'kubejobs', 'plugin_info': {'termination_grace_period_seconds': 0, 'password': 'senha', 'username': 'admin', 'control_plugin': 'kubejobs', 'enable_visualizer': True, 'monitor_info': {'expected_time': 20}, 'env_vars': {}, 'img': IMG, 'redis_workload': '', 'visualizer_info': {'datasource_type': 'influxdb'}, 'init_size': 1, 'job_resources_lifetime': 800, 'visualizer_plugin': 'k8s-grafana', 'enable_detailed_report': True, 'cmd': ['python', '/app/run.py'], 'control_parameters': {'metric_source': 'redis', 'actuator': 'k8s_replicas',}, 'monitor_plugin': 'kubejobs'}, 'enable_auth': False}

	job_json["plugin_info"]["redis_workload"] = workload_url
	job_json["plugin_info"]["monitor_info"]["expected_time"] = expected_time

	job_json = strategy_pid(job_json)
	r = requests.post(SUBMIT_ENDPOINT, json=job_json)

	return r.json()["job_id"]

def str2bool(value):
	yes_str = ["y", "yes"]

	return value.lower() in yes_str

def sort_experiment_data(json_data):
	sorted_data = []

	for item in json_data.items():
		item_time = datetime.datetime.strptime(item[0], "%Y-%m-%dT%H:%M:%SZ").timestamp()
		sorted_data.append([item_time, item[1]["replicas"], 
			item[1]["output_flux"], item[1]["job_progress"] * 100,
			item[1]["error"], item[1]["time_progress"]])

	sorted_data.sort(key=lambda x: x[0])

	starting_time = sorted_data[0][0]

	completed_index = 0

	for i in range(0, len(sorted_data)):
		sorted_data[i][0] = sorted_data[i][0] - starting_time

		if sorted_data[i][3] == 100:
			completed_index = i
			break

	for i in range(completed_index + 1, len(sorted_data)):
		sorted_data.pop()

	return sorted_data
	
def save_csv(execution_data, file):
	with open(file, "w+") as new_file:
		new_file.write("#timestamp, replicas, output_flux, job_progress, error, time_progress\n")
		
		for item in execution_data:
			new_file.write(f"{item[0]}, {item[1]}, {item[2]}, {item[3]}, {item[4]}, {item[5]}\n")

def check_report(job_id):
	r = requests.get(REPORT_ENDPOINT.format(job_id))
	r_json = r.json()

	try:
		if r_json["message"]:
			return False
	except:
		return r_json

def plot_results(expected_time, sorted_data):
	data_to_plot = []

	last_progress = 0
	last_time = 0
	interval = 0

	for item in sorted_data:
		progress = item[3]
		time_now = item[0]

		interval = time_now - last_time
		last_time = time_now

		jpps = 0

		if interval > 0:
			jpps = (progress - last_progress) / interval
			# For some reason Asperathos is returning a non-constant interval
			# Maybe it is rounding the decimal values
			#jpps = (progress - last_progress) / 2

		last_progress = progress
	
		model = {
			"time": time_now,
			"job_progress": progress,
			"jpps": jpps,
			"replicas": item[1],
			"output_flux": item[2],
			"error": item[4],
			"setpoint": item[5]
		}

		data_to_plot.append(model)

		if progress == 100:
			break

	print("100% on {} seconds.".format(last_time))
	generate_plots(f"Execution for expected time = {expected_time} seconds", data_to_plot)

if __name__ == "__main__":
	args = parser.parse_args()

	job_id = submit_job(args.expected_time, WORKLOADS[args.workload][0])
	execution_result = False

	print("Running with expected time = {}...".format(args.expected_time))

	while execution_result is False:
		execution_result = check_report(job_id)
		time.sleep(1)

	sorted_data = sort_experiment_data(execution_result)
	timestamp = int(time.time())

	file_dir = f"{args.dir}/{timestamp}-expected{args.expected_time}-wl{WORKLOADS[args.workload][1]}.csv"

	save_csv(sorted_data, file_dir)

	if str2bool(args.plot):
		plot_results(args.expected_time, sorted_data)
