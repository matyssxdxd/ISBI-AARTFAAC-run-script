import re
from datetime import datetime, timedelta
from collections import defaultdict
from bitstream import *
from vex import Vex
import sys

class VEXParser:
    def __init__(self):
        self.data = defaultdict(dict)
        self.current_section = None
        self.current_subsection = None

    def parse(self, vex_file):
        with open(vex_file, 'r') as file:
            for line in file:
                line = line.strip()

                section_match = re.match(r"^\$(\w+);", line)
                if section_match:
                    self.current_section = section_match.group(1)
                    continue

                subsection_match = re.match(r"(def|scan) (\S+);", line)
                if subsection_match:
                    self.current_subsection = subsection_match.group(2)
                    self.data[self.current_section][self.current_subsection] = {}
                    continue

                subsection_end = re.match(r"(enddef|endscan);", line)
                if subsection_end:
                    self.current_subsection = None
                    continue


                if self.current_section and self.current_subsection:
                    match = re.match(r"(\w+)\s*=\s*(.+?);", line)

                    if match:
                        key = match.group(1)
                        value = match.group(2)
                        self.data[self.current_section][self.current_subsection].setdefault(key, []).append(value)
                        continue

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


vex_parser = VEXParser()
vex_parser.parse(sys.argv[1])
threads = vex_parser.data["THREADS"]["IrIbThreads#0"]["channel"]
mappedIdx = [0 for _ in range(len(threads))]
for i in range(len(threads)):
    thread = threads[i].split()
    threadIdx = int(thread[-1])
    mappedIdx[threadIdx] = i

print(mappedIdx)
date_str = (str(vex_parser.data["SCHED"]["No0003"]["start"][0]))
print(date_str)

match = re.match(r"(\d+)y(\d+)d(\d+)h(\d+)m(\d+)s", date_str)
formatted_date = ""

if match:
    years = int(match.group(1))
    days = int(match.group(2))
    hours = int(match.group(3))
    minutes = int(match.group(4))
    seconds = int(match.group(5))

    base_date = datetime(years, 1, 1)

    total_days = days

    time_delta = timedelta(days=total_days, hours=hours, minutes=minutes, seconds=seconds)

    final_date = base_date + time_delta

    formatted_date = final_date.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_date)

runtime = vex_parser.data["FREQ"]
print(runtime)
# sample_rate = str(10)
# vdif_1 = str(10)
# vdif_2 = str(10)
# cmd = "TZ=UTC ISBI/ISBI -p1 -n2 -t12512 -c256 -c255 -b16 -s8 -m15 -D '" + formatted_date + "' -r" + runtime + " -g0 -q1 -R0 -B0 -f" + sample_rate + " -i " + vdif_1 + "," + vdif_2;
# print(cmd)
