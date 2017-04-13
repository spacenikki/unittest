import re

stop_on_error = False

host_pattern = "(?P<host>[^\s]+)"
datetime_pattern = "(?P<datetime>[^\]]+)"
http_pattern = "(\05\01|(?P<method>[^\s]+)(\s+)(?P<path>[^\s]+)([^\"]*))"  # \05\01 ==> junk character?


line_pattern = re.compile(host_pattern + ' - - \[' + datetime_pattern + '\] ("' + http_pattern + '") (?P<code>\d+) (?P<bytes>\d+|-)')
line_number = 0

class Event():
    bytes = None
    code = None
    datetime = None
    host = None
    method = None
    path = None

    def __init__(self, line):
        global line_pattern, line_number, stop_on_error
        line_number += 1

        match = re.match(line_pattern, line)
        if (match is None):
            error = "Error creating Event at line #" + str(line_number) + ": " + line
            if stop_on_error:
                raise Exception(error)
            else:
                print(error)
        else:
            groups = match.groupdict()
            self.bytes = 0 if groups['bytes'] == '-' else groups['bytes']
            self.code = groups['code']
            self.datetime = groups['datetime']
            self.host = groups['host']
            self.method = groups['method']
            self.path = groups['path']
            self.line = line  # whole line for feature 4


def read_file(filename):
    with open(filename) as server_log:
        lines = server_log.readlines()

        # for line in lines:
        #     if re.search(r'(\d+/\w+/\d+)?:(\d+:\d+:\d+)? (-\d+)?(?=])', line, re.M|re.I): # found  # date, time, timezone!
        #         timestamp = re.search(r'(\d+/\w+/\d+)?:(\d+:\d+:\d+)? (-\d+)?(?=])', line, re.M|re.I)  
        #         # Event.timestamp = timestamp.group(0)
        #         Event.date = timestamp.group(1)
        #         Event.time = timestamp.group(2 )
        #         Event.timezone = timestamp.group(3)

        
        events = map(Event, lines)   # create class "Event"
        return events   


