import os
os.environ["MAVLINK20"] = "1"
from pymavlink import mavutil
import csv, sys

mission_type = int(sys.argv[3])
file_name = sys.argv[2]
with open(file_name) as csv_file:
    data = csv.reader(csv_file)
    waypoints = list(data)

#print(waypoints)
master = mavutil.mavlink_connection(device=sys.argv[1], source_system=255)
master.recv_match(type="HEARTBEAT", blocking=True)
print("heartbeat recv", master.mavlink20())
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
