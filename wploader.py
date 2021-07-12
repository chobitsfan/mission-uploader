import os
os.environ["MAVLINK20"] = "1"
from pymavlink import mavutil
import csv, sys
import serial.tools.list_ports

file_name = sys.argv[1]
with open(file_name) as csv_file:
    data = csv.reader(csv_file)
    waypoints = list(data)
mission_type = 0
if waypoints[0][3] == "5000":
    print("fence")
    mission_type = 1

com_ports = serial.tools.list_ports.comports()
apm_com_port = ""
for com_port in com_ports:
    if com_port.description.startswith("ArduPilot MAVLink"):
        print(com_port.description)
        apm_com_port = com_port.device
        break
if apm_com_port == "":
    print("cannot find FC com port")
    quit()

#print(waypoints)
master = mavutil.mavlink_connection(device=apm_com_port, source_system=255)
#need to send something for network
#master.mav.heartbeat_send(6, 0, 0, 0, 0)
master.recv_match(type="HEARTBEAT", blocking=True)
print("heartbeat recv", master.mavlink20())
if mission_type == 1:
    master.mav.param_set_send(0, 0, "FENCE_ALT_MAX".encode('utf8'), int(waypoints[0][10])*0.01, 9)
msg = master.recv_match(type="PARAM_VALUE", blocking=True)
print("fence_alt_max", msg.param_value)
master.mav.mission_count_send(0, 0, len(waypoints), mission_type)
while True:
    try:
        msg = master.recv_msg()
    except KeyboardInterrupt:
        break
    if msg is not None:
        msg_type = msg.get_type()
        if msg_type == "MISSION_REQUEST_INT" or msg_type == "MISSION_REQUEST":
            print("recv", msg_type, msg.seq)
            wp = waypoints[msg.seq]
            master.mav.mission_item_int_send(0, 0, msg.seq, 0, int(wp[3]), 0, 1, float(wp[4]), float(wp[5]), float(wp[6]), float(wp[7]), int(wp[8]), int(wp[9]), float(wp[10]), mission_type)
        elif msg_type == "MISSION_ACK":
            print("recv ack", msg.type)
            break
        elif msg_type == "STATUSTEXT":
            print(msg.text)
        #else:
        #    print(msg_type)
