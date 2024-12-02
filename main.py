import re
from datetime import datetime, timedelta
from collections import defaultdict
from bitstream import *
from vex import Vex
import sys

vex = Vex(sys.argv[1])
if "THREADS" in vex:
	print("WOOHOO")
else:
	BITSTREAMS, THREADS, modes = create_bitstreams_and_threads_block(sys.argv[1])
	print(THREADS[0])
	file = open(sys.argv[1], 'a')
	file.write("*------------------------------------------------------------------------------")
	file.write(THREADS[0])
	file.close()


vex = Vex(sys.argv[1])
threads = vex["THREADS"]["IrIbThreads#0"].getall("channel")
mappedIdx = [0 for _ in range(len(threads))]
for i in range(len(threads)):
    thread = threads[i]
    threadIdx = int(thread[-1])
    mappedIdx[threadIdx] = i

observation = "No0003"
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
print(formatted_date)

freq = vex["MODE"][sys.argv[1].split(".")[0]]["FREQ"][0]

sample_rate = str(int(float(vex["FREQ"][freq]["sample_rate"].split()[0]) * 1e+6))
runtime = str(180)
vdif_1 = str(10)
vdif_2 = str(10)
mapping = ' '.join(str(x) for x in mappedIdx)
cmd = "TZ=UTC ISBI/ISBI -M " + mapping  +" -p1 -n2 -t12512 -c256 -c255 -b16 -s8 -m15 -D '" + formatted_date + "' -r" + runtime + " -g0 -q1 -R0 -B0 -f" + sample_rate + " -i " + vdif_1 + "," + vdif_2;
print(cmd)
