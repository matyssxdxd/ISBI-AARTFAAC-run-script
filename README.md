# ISBI AARTFAAC run script (WIP)
ISBI AARTFAAC run scrip is a python script that takes in VEX file and control file as arguments and generates a command
to run or runs the ISBI AARTFAAC correlator. The code requires [Python3](https://www.python.org/downloads/) and 
[MultiDict](https://multidict.aio-libs.org/en/stable/) library.
## Control file format
```json
{
"start-time":"0",
"end-time":"60",
"file-path-ir":"test1.vdif",
"file-path-ib":"test2.vdif",
"correlation-channels": [1, 2, 3, 4, 5, 6, 7, 8],
"output-path": "/out/",
"reference-station": "some station"
}
```
- **start-time:** time (seconds) since the observation's start time when the correlator should start correlating.
- **end-time:** time (seconds) for how many seconds correlator should correlate.
- **file-path-ir:** path to the IR telescope [VDIF](https://vlbi.org/wp-content/uploads/2019/03/2009.06.25_Whitney_e-VLBI_wkshop-Madrid.pdf) file.
- **file-path-ib:** path to the IB telescope [VDIF](https://vlbi.org/wp-content/uploads/2019/03/2009.06.25_Whitney_e-VLBI_wkshop-Madrid.pdf) file.
- **correlation-channels:** correlation channels.
- **output-path:**: path where correlator output will be saved.
- **reference-station:** reference station.
## Usage
```shell
python3 main.py -v VEX_FILE.vex -c CTRL_FILE.json
```