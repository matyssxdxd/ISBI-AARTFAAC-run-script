from datetime import datetime, timedelta
from bitstream import *
from vex import Vex
import argparse
import json
import sys
import re
import subprocess

# TODO: Check if CTRL file is correct (start-time, end-time, file paths, etc.)
#		Make the code work for ANY vex file.
#		Allow vex file to not be provided???
#		Implement an option to generate a run command OR to run the correlator

def get_scan_nr(vex, ctrl):
    vdif_1 = ctrl["file-path-ir"]
    vdif_2 = ctrl["file-path-ib"]

    scan_nr_1 = re.search(r"no\d+", vdif_1) 
    scan_nr_2 = re.search(r"no\d+", vdif_2)

    if not scan_nr_1 or not scan_nr_2:
        sys.exit("VDIF file name should contain the scan number.")

    if scan_nr_1.group() != scan_nr_2.group():
        sys.exit("Scan numbers should be the same for both VDIF files.")

    return scan_nr_1.group()

def get_start_time(vex, scan_nr):
    date_str = vex["SCHED"][scan_nr.capitalize()]["start"]

    years = int(date_str[:4])
    days = int(date_str[5:8])
    hours = int(date_str[9:11])
    minutes = int(date_str[12:14])
    seconds = int(date_str[15:17])

    base_date = datetime(years, 1, 1)
    time_delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    final_date = base_date + time_delta
    formatted_date = final_date.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_date

def get_sample_rate(vex):
    dict_key = list(vex["MODE"].keys())[0]
    freq = vex["MODE"][dict_key]["FREQ"][0]
    sample_rate = str(int(float(vex["FREQ"][freq]["sample_rate"].split()[0]) * 1e+6))

    return sample_rate

def get_runtime(vex, ctrl, scan_nr):
    start_time = int(control["start-time"])
    end_time = int(control["end-time"])

    if start_time < 0 or end_time < 0:
        sys.exit("Start-time and end-time should be a positve integer.")

    if start_time > end_time:
        sys.exit("Start-time should not be greater than end-time.")

    observation_length = int(vex["SCHED"][scan_nr.capitalize()]["station"][2].split()[0])
    
    if (observation_length - (start_time + end_time)) < 0:
        sys.exit(f"Observation length is {observation_length}s, while start-time and end-time sum provided exceeds it.")
    
    return str(end_time - start_time)

def get_subbands(vex):
    dict_key = list(vex["MODE"].keys())[0]
    
    return vex["MODE"][dict_key]["BBC"][0].removesuffix("BBCs")

def generate_threads_block(vex_path):
    bitstreams, threads, modes = create_bitstreams_and_threads_block(vex_path)
    file = open(vex_path, 'a')
    file.write("*------------------------------------------------------------------------------")
    file.write(threads[0])
    file.close()

def get_channel_mapping(vex_path):
    vex = Vex(vex_path)
    if not "THREADS" in vex:
        generate_threads_block(vex_path)

    vex = Vex(vex_path)
    threads = vex["THREADS"]["IrIbThreads#0"].getall("channel")
    mapped_idx = [0 for _ in range(len(threads))]

    for i in range(len(threads)):
        thread = threads[i]
        thread_idx = int(thread[-1])
        mapped_idx[thread_idx] = i

    return " ".join(str(x) for x in mapped_idx)

def generate_output_cmd(ctrl, scan_nr, channel_mapping, start_time, runtime, sample_rate, subbands):
    output = "-o "
    for i in range(int(subbands)):
        output += f"{ctrl["output-path"]}{scan_nr}_{i + 1}.out"
        if (i < int(subbands) - 1):
            output += ","

    cmd = f"TZ=UTC ISBI/ISBI -M {channel_mapping} -p1 -n2 -t12512 -c256 -c255 -b16 -s{subbands} -m15 -D {start_time} -r{runtime} -g0 -q1 -R0 -B0 -f{sample_rate} -i {ctrl["file-path-ir"]},{ctrl["file-path-ib"]} {output}"

    return cmd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vex", help="Observation's VEX file")
    parser.add_argument("-c", "--control", help="Control file")
    parser.add_argument('--cmd', action=argparse.BooleanOptionalAction)
 
    args = parser.parse_args()
    
    file = open(args.control, 'r')
    control = json.load(file)
    file.close()

    vex = Vex(args.vex)

    scan_nr = get_scan_nr(vex, control)
    start_time = get_start_time(vex, scan_nr)
    sample_rate = get_sample_rate(vex)
    runtime = get_runtime(vex, control, scan_nr)
    subbands = get_subbands(vex)
    channel_mapping = get_channel_mapping(args.vex)

    if args.cmd:
        print(generate_output_cmd(control, scan_nr, channel_mapping, start_time, runtime, sample_rate, subbands))
    else:
        print(subprocess.check_output(generate_output_cmd(control, scan_nr, channel_mapping, start_time, runtime, sample_rate, subbands)))