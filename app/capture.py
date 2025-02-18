import argparse
from datetime import datetime as dt
import re
import serial
from serial.tools import list_ports
import time

DEFAULT_USB_REGEX = r"/dev/.+serial.+"
DEFAULT_OUTPUT_REGEX = r'^\d+,\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+\.\d+,\d+\.\d+,\d+\.\d+,\d+\.\d+.*$'
SLEEP_ON_CONNECTION_TIME = 3

def get_port(args):
    port = args.port
    if not port:
        ports = list(list_ports.grep(DEFAULT_USB_REGEX))
        if not ports:
            raise ValueError("No default port found")
        port = ports[0].device
    ser = serial.Serial(port, args.baudrate, timeout=args.timeout)
#    ser.readline()
#    time.sleep(SLEEP_ON_CONNECTION_TIME)
#    print(f"Connecting to {ser}")
    return ser


def parse_arguments():
    parser = argparse.ArgumentParser(description="Captures PowerProfiler USB output")
    parser.add_argument("-t", "--time", 
                        type=float, default=10, 
                        help="Specify time in seconds (default: 10).\n"
                        "If zero, don't stop")
    parser.add_argument("-p", "--port", 
                        type=str, default=None, 
                        help="Specify USB port (default, first serial found)")
    parser.add_argument("-b", "--baudrate",
                        type=int, default=115200,
                        help="Baud rate (default 115200)")
    parser.add_argument("-u", "--timeout",
                        type=int, default=3,
                        help="Serial port timeout (default 3s)")
    parser.add_argument("--header",
                        type=bool, default=True,
                        action=argparse.BooleanOptionalAction,
                        help="Include header on output")
    parser.add_argument("--filter", 
                        type=bool, default=True,
                        action=argparse.BooleanOptionalAction,
                        help="Filter by Regex (default True)")
    args = parser.parse_args()
    return args
    

def main():
    args = parse_arguments()
    ser = get_port(args)

    if args.header:
        print("index,read_at,millis,timestamp,voltage,current,power,bus_voltage")
    index = 0
    start = time.time()
    while args.time == 0 or (time.time() - start < args.time):
        line = ser.readline()
        read_at = dt.now()
        try:
            sline = line.decode('utf-8')
            if not args.filter or re.match(DEFAULT_OUTPUT_REGEX, sline):
                print(f"{index},{read_at},{sline.strip()}")
                index += 1
        except UnicodeDecodeError:
            continue

    if ser:
        ser.close()


if __name__ == "__main__":
    main()

