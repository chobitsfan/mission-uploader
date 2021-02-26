import os
os.environ["MAVLINK20"] = "1"
from pymavlink import mavutil
import csv, sys

mission_type = int(sys.argv[3])
file_name = sys.argv[2]

master = mavutil.mavlink_connection(device=sys.argv[1], source_system=255)
master.recv_match(type="HEARTBEAT", blocking=True)
print("recv heartbeat", master.mavlink20())
master.mav.mission_request_list_send(0, 0, mission_type)
mission_count = -1
expect_seq = 0
while True:
    try:
        msg = master.recv_msg()
    except KeyboardInterrupt:
        break
    if msg is not None:
        msg_type = msg.get_type()
        if msg_type == "MISSION_COUNT":
            mission_count = msg.count
            if mission_count > 0:
                master.mav.mission_request_int_send(0, 0, 0, mission_type)
            else:
                print("no mission")
        elif msg_type == "MISSION_ITEM_INT":
            if msg.seq == expect_seq:
                print("recv mission item", msg.seq)
                expect_seq = expect_seq + 1
                if expect_seq < mission_count:
                    master.mav.mission_request_int_send(0, 0, expect_seq, mission_type)
                else:
                    master.mav.mission_ack_send(0, 0, 0, mission_type)
                    print("done")
                    break