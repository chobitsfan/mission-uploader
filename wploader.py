from pymavlink import mavutil
import csv, sys

with open(sys.argv[2]) as csv_file:
    data = csv.reader(csv_file)
    waypoints = list(data)

print(waypoints)
master = mavutil.mavlink_connection(device=sys.argv[1], source_system=255)
master.recv_match(type="HEARTBEAT", blocking=True)
print("heartbeat recv")
master.mav.mission_count_send(0, 0, len(waypoints))
while True:
    try:
        msg = master.recv_msg()
    except KeyboardInterrupt:
        break
    if msg is not None:
        msg_type = msg.get_type()
        if msg_type == "MISSION_REQUEST_INT" or msg_type == "MISSION_REQUEST":
            print("send", msg.seq)
            wp = waypoints[msg.seq]
            master.mav.mission_item_int_send(0, 0, msg.seq, 0, int(wp[3]), 0, 1, float(wp[4]), float(wp[5]), float(wp[6]), float(wp[7]), int(wp[8]), int(wp[9]), float(wp[10]))
        elif msg_type == "MISSION_ACK":
            print("finished", msg.type)
            break
        #else:
        #    print(msg_type)
