from JumpScale.core.InitBase import *

import argparse

#import sys
# port=sys.argv[1]
# key=sys.argv[2]

parser = argparse.ArgumentParser("Start an appserver6 worker (qworker)")

# parser.add_argument("-n", "--worker-number", dest="workernr", required=True,
        # type=int, help="The number of this worker")
parser.add_argument("-p", "--port", dest="port", default=9100,
                    type=int, help="The TCP port for this worker", required=True)
parser.add_argument("-s", "--secret", dest="secret", help="The secret", required=True)

args = parser.parse_args()

socketserver = j.system.socketserver.get(int(args.port), str(args.secret))

j.application.start("worker")


def handledata(data):
    code, params = j.tools.json.decode(data)
    try:
        result = j.system.process.executeCode(code, params)
        result = ["OK", result]
    except Exception as e:
        result = ["ERROR", str(e)]

    return j.tools.json.encode(result)

socketserver.setDataHandler(handledata)

socketserver.start()

j.application.stop()
