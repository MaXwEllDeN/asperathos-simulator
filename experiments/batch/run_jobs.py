#!/usr/bin/python
import json
import time
import requests
import argparse
import datetime
from aspplots import generate_plots

SUBMIT_ENDPOINT = "http://0.0.0.0:1500/submissions"
REPORT_ENDPOINT = "http://0.0.0.0:1500/submissions/{}/report"

WORKLOADS = ["https://gist.githubusercontent.com/MaXwEllDeN/\
2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt",

"https://gist.githubusercontent.com/MaXwEllDeN/\
88f6975f8f089b69a4a1d530e9b77236/raw/4b2b6fc64177c5232dc4e67703d6a350e7fdee39/workload800.txt"
]

# WORKLOADS
# 0: 327 items
# 1: 800 items

parser = argparse.ArgumentParser()
parser.add_argument("expected_time", help="Expected execution time.", type=int)
parser.add_argument("workload", help="Workload.", type=int)
parser.add_argument("dir", help="Directory file.")
parser.add_argument("plot")

def submit_job(expected_time, workload_url):
	job_json = {'plugin': 'kubejobs', 'plugin_info': {'password': 'senha', 'username': 'admin', 'control_plugin': 'kubejobs', 'enable_visualizer': True, 'monitor_info': {'expected_time': 20}, 'env_vars': {}, 'img': 'maxwellden/quickstart:demo', 'redis_workload': '', 'visualizer_info': {'datasource_type': 'influxdb'}, 'init_size': 1, 'job_resources_lifetime': 800, 'visualizer_plugin': 'k8s-grafana', 'enable_detailed_report': True, 'cmd': ['python', '/app/run.py'], 'control_parameters': {'metric_source': 'redis', 'min_rep': 7, 'trigger_up': 0, 'actuation_size': 1, 'schedule_strategy': 'default', 'actuator': 'k8s_replicas', 'trigger_down': 0, 'max_size': 10, 'heuristic_options': {'derivative_gain': 0, 'proportional_gain': 0.1, 'integral_gain': 0}, 'check_interval': 5, 'max_rep': 7}, 'monitor_plugin': 'kubejobs'}, 'enable_auth': False}

	job_json["plugin_info"]["monitor_info"]["expected_time"] = expected_time
	job_json["plugin_info"]["control_parameters"]["min_rep"] = 1
	job_json["plugin_info"]["control_parameters"]["max_rep"] = 1
	job_json["plugin_info"]["control_parameters"]["actuation_size"] = 1
	job_json["plugin_info"]["control_parameters"]["check_interval"] = 2
	#job_json["plugin_info"]["control_parameters"]["check_interval"] = 0.5 <- Asperathos will automatically round down to zero
	job_json["plugin_info"]["redis_workload"] = workload_url
        
	r = requests.post(SUBMIT_ENDPOINT, json=job_json)

	return r.json()["job_id"]

def str2bool(value):
	yes_str = ["y", "yes"]

	return value.lower() in yes_str

def save_csv(json_data, file):
	sorted_data = []

	for item in json_data.items():
		item_time = datetime.datetime.strptime(item[0], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
		sorted_data.append((item_time, item[1]["job_progress"] * 100, item[1]["replicas"], item[1]["error"], item[1]["time_progress"]))

	sorted_data.sort(key=lambda x: x[0])

	with open(file, "w+") as new_file:
		new_file.write("#timestamp, job_progress, replicas, error, time_progress\n")
		
		for item in sorted_data:
			new_file.write("{}, {}, {}, {}, {}\n".format(item[0], item[1], item[2], item[3], item[4]))

def check_report(job_id):
	r = requests.get(REPORT_ENDPOINT.format(job_id))
	r_json = r.json()

	try:
		if r_json["message"]:
			return False
	except:
		return r_json

def plot_results(expected_time, execution_result):
	sorted_data = []
	print(execution_result)

	for item in execution_result.items():
		item_time = datetime.datetime.strptime(item[0], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
		sorted_data.append((item_time, item[1]["job_progress"] * 100, item[1]["replicas"], item[1]["error"], item[1]["time_progress"]))

	sorted_data.sort(key=lambda x: x[0])

	data_to_plot = []
	starting_time = sorted_data[0][0]

	last_progress = 0
	last_time = 0
	interval = 0

	for item in sorted_data:
		progress = item[1]
		time_now = item[0] - starting_time

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
			"replicas": item[2],
			"error": item[3],
			"setpoint": item[4]
		}

		data_to_plot.append(model)

		if progress == 100:
			break

	print("100% on {} seconds.".format(last_time))
	generate_plots(f"Execution for expected time = {expected_time} seconds", data_to_plot)

if __name__ == "__main__":
	args = parser.parse_args()

	job_id = submit_job(args.expected_time, WORKLOADS[args.workload])
	execution_result = False

	print("Running with expected time = {}...".format(args.expected_time))

	while execution_result is False:
		execution_result = check_report(job_id)
		time.sleep(1)

	file_dir = "{}/{}-expected{}.csv".format(args.dir, int(time.time()), args.expected_time)
	save_csv(execution_result, file_dir)

	if str2bool(args.plot):
		plot_results(args.expected_time, execution_result)
