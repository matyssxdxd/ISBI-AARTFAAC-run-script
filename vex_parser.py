import re
from collections import defaultdict

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
                    self.current_section = section_match[1]
                    continue

                subsection_match = re.match(r"(def|scan) (\S+);", line)
                if subsection_match:
                    self.current_subsection = subsection_match[2]
                    self.data[self.current_section][self.current_subsection] = {}
                    continue

                subsection_end = re.match(r"(enddef|endscan);", line)
                if subsection_end:
                    self.current_subsection = None
                    continue


                if self.current_section and self.current_subsection:
                    match = re.match(r"(\w+)\s*=\s*(.+?);", line)

                    if match:
                        key = match[1]
                        value = match[2]
                        self.data[self.current_section][self.current_subsection].setdefault(key, []).append(value)
                        continue

vex = VEXParser()
vex.parse("I001.vix")
print(vex.data)
