import time
import json
import datetime
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("input_json", help="Path to the json containing the execution data.")
parser.add_argument("output_csv", help="CSV file to be generated.")

if __name__ == "__main__":
	args = parser.parse_args()
	sorted_data = []
	with open(args.input_json, "r") as file:
		json_data = json.loads(file.read())
		for item in json_data.items():
			item_time = time.mktime(datetime.datetime.strptime(item[0], "%Y-%m-%dT%H:%M:%SZ").timetuple())
			sorted_data.append((item_time, item[1]))
	
	sorted_data.sort(key=lambda x: x[0])
	
	with open(args.output_csv, "w+") as file:
		file.write("#time, time_progress, job_progress, replicas, error\n")
		for item in sorted_data:
			new_time = item[0] - sorted_data[0][0]
			file.write("{},{},{},{},{}\n".format(new_time, item[1]["time_progress"], item[1]["job_progress"], item[1]["replicas"], item[1]["error"]))
