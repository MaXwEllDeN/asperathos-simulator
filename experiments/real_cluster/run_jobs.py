#!/usr/bin/python
import json
import time
import requests
import argparse
import datetime
from aspplots import generate_plots

SUBMIT_ENDPOINT = "http://0.0.0.0:1500/submissions"
REPORT_ENDPOINT = "http://0.0.0.0:1500/submissions/{}/report"

parser = argparse.ArgumentParser()
parser.add_argument("step", help="Step amplitude.", type=int)
parser.add_argument("dir", help="Directory file.")
parser.add_argument("plot")

def submit_job(steps=1):
	job_json = {'plugin': 'kubejobs', 'plugin_info': {'password': 'senha', 'username': 'admin', 'control_plugin': 'kubejobs', 'enable_visualizer': True, 'monitor_info': {'expected_time': 20}, 'env_vars': {}, 'img': 'maxwellden/quickstart:demo', 'redis_workload': '', 'visualizer_info': {'datasource_type': 'influxdb'}, 'init_size': 1, 'job_resources_lifetime': 800, 'visualizer_plugin': 'k8s-grafana', 'enable_detailed_report': True, 'cmd': ['python', '/app/run.py'], 'control_parameters': {'metric_source': 'redis', 'min_rep': 7, 'trigger_up': 0, 'actuation_size': 1, 'schedule_strategy': 'default', 'actuator': 'k8s_replicas', 'trigger_down': 0, 'max_size': 10, 'heuristic_options': {'derivative_gain': 0, 'proportional_gain': 0.1, 'integral_gain': 0}, 'check_interval': 5, 'max_rep': 7}, 'monitor_plugin': 'kubejobs'}, 'enable_auth': False}

	job_json["plugin_info"]["control_parameters"]["min_rep"] = steps
	job_json["plugin_info"]["control_parameters"]["max_rep"] = steps
	job_json["plugin_info"]["control_parameters"]["max_rep"] = steps
	job_json["plugin_info"]["control_parameters"]["check_interval"] = 0.5
	job_json["plugin_info"]["redis_workload"] = "https://gist.githubusercontent.com/MaXwEllDeN/2a1b9bb13dae44241e358e14b585da6f/raw/654c4f29af5d751ff0a9079b5be72305175ad501/workload327.txt"

	r = requests.post(SUBMIT_ENDPOINT, json=job_json)

	return r.json()["job_id"]

def str2bool(value):
	return value == "y"

def save_csv(json_data, file):
	sorted_data = []

	for item in json_data.items():
		item_time = time.mktime(datetime.datetime.strptime(item[0], "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())
		sorted_data.append((item_time, item[1]["job_progress"] * 100, item[1]["replicas"], item[1]["error"], item[1]["time_progress"]))

	sorted_data.sort(key=lambda x: x[0])

	with open(file, "w+") as new_file:
		new_file.write("timestamp, job_progress, replicas, error, time_progress\n")
		
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


if __name__ == "__main__":
	args = parser.parse_args()

	job_id = submit_job(args.step)
	execution_result = False

	print("Running with step = {}...".format(args.step))

	while execution_result is False:
		execution_result = check_report(job_id)
		time.sleep(1)

	file_dir = "{}/{}-step{}.csv".format(args.dir, int(time.time()), args.step)

	save_csv(execution_result, file_dir)

	if str2bool(args.plot):
		sorted_data = []
	
		for item in execution_result.items():
			item_time = time.mktime(datetime.datetime.strptime(item[0], "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())
			#item_time = time.mktime(datetime.datetime.strptime(item[0], "%Y-%m-%dT%H:%M:%SZ").timetuple())
			sorted_data.append((item_time, item[1]["job_progress"] * 100))
	
		sorted_data.sort(key=lambda x: x[0])
	
		data_to_plot = []
		starting_time = sorted_data[0][0]
	
		last_progress = 0
		last_time = 0
		interval = 0
		jpps_array = []
	
		for item in sorted_data:
			progress = item[1]
			time_now = item[0] - starting_time
	
			interval = time_now - last_time
			last_time = time_now
	
			jpps = 0
	
			if interval > 0:
				jpps = (progress - last_progress) / interval
	
			last_progress = progress
	
			jpps_array.append(jpps)
			avg_jpps = sum(jpps_array) / len(jpps_array)
	
			model = {
				"time": time_now,
				"job_progress": progress,
				"avg_jpps": avg_jpps,
				"completed": progress,
				"setpoint": 0,
				"avg_setpoint": 0
			}
	
			data_to_plot.append(model)
	
		print("100% on {} seconds.".format(last_time))
		generate_plots(data_to_plot)
