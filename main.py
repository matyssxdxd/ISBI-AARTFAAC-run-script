from datetime import datetime, timedelta
from bitstream import *
from vex import Vex
import argparse
import json

# TODO: Check if CTRL file is correct (start-time, end-time, file paths, etc.)
#		Make the code work for ANY vex file.
#		Allow vex file to not be provided???
#		Implement an option to generate a run command OR to run the correlator

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--vex", help="Observation's VEX file")
parser.add_argument("-c", "--control", help="Control file")

args = parser.parse_args()

file = open(args.control, 'r')
control = json.load(file)
file.close()




vex = Vex(args.vex)

if "THREADS" in vex:
    print("WOOHOO")
else:
	BITSTREAMS, THREADS, modes = create_bitstreams_and_threads_block(sys.argv[1])
	print(THREADS[0])
	file = open(args.vex, 'a')
	file.write("*------------------------------------------------------------------------------")
	file.write(THREADS[0])
	file.close()


vex = Vex(args.vex)
threads = vex["THREADS"]["IrIbThreads#0"].getall("channel")
mappedIdx = [0 for _ in range(len(threads))]
for i in range(len(threads)):
    thread = threads[i]
    threadIdx = int(thread[-1])
    mappedIdx[threadIdx] = i

observation = "No0002"
date_str = vex["SCHED"][observation]["start"]

years = int(date_str[:4])
days = int(date_str[5:8])
hours = int(date_str[9:11])
minutes = int(date_str[12:14])
seconds = int(date_str[15:17])

base_date = datetime(years, 1, 1)
time_delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
final_date = base_date + time_delta
formatted_date = final_date.strftime("%Y-%m-%d %H:%M:%S")

# This will not work for ALL of the files, need to think of a better way to retrieve this data
freq = vex["MODE"][args.vex.split(".")[0]]["FREQ"][0]
sample_rate = str(int(float(vex["FREQ"][freq]["sample_rate"].split()[0]) * 1e+6))

runtime = str(int(control["end-time"]) - int(control["start-time"]))
vdif_1 = control["file-path-ir"]
vdif_2 = control["file-path-ib"]
mapping = ' '.join(str(x) for x in mappedIdx)
subbands = 8
output = "-o "

for i in range(subbands):
	output += f"{control["output-path"]}{observation}_{i + 1}.out"
	if (i < subbands - 1):
		output += ","

cmd = "TZ=UTC ISBI/ISBI -M " + mapping  +" -p1 -n2 -t12512 -c256 -c255 -b16 -s8 -m15 -D '" + formatted_date + "' -r" + runtime + " -g0 -q1 -R0 -B0 -f" + sample_rate + " -i " + vdif_1 + "," + vdif_2 + " " + output;
print(cmd)
