import os
os.environ["MAVLINK20"] = "1"
from pymavlink import mavutil
import csv, sys
import serial.tools.list_ports

com_ports = serial.tools.list_ports.comports()
apm_com_port = ""
for com_port in com_ports:
    if com_port.description.startswith("ArduPilot MAVLink"):
        print(com_port.description)
        apm_com_port = com_port.device
        break
if apm_com_port == "":
    for com_port in com_ports:
        if com_port.description.startswith("ArduPilot"):
            print(com_port.description)
            apm_com_port = com_port.device
            break
if apm_com_port == "":
    print("cannot find FC com port")
    quit()

mission_type = int(sys.argv[2])
file_name = sys.argv[1]

master = mavutil.mavlink_connection(device=apm_com_port, source_system=255)
master.recv_match(type="HEARTBEAT", blocking=True)
print("recv heartbeat", master.mavlink20())
master.mav.mission_request_list_send(0, 0, mission_type)
mission_count = -1
expect_seq = 0
csv = []
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
                csv.append(str(msg.seq)+","+str(msg.current)+","+str(msg.frame)+","+str(msg.command)+","+str(msg.param1)+","+str(msg.param2)+","+str(msg.param3)+","+str(msg.param4)+","+str(msg.x)+","+str(msg.y)+","+str(msg.z)+","+str(msg.autocontinue)+"\n")
                expect_seq = expect_seq + 1
                if expect_seq < mission_count:
                    master.mav.mission_request_int_send(0, 0, expect_seq, mission_type)
                else:
                    master.mav.mission_ack_send(0, 0, 0, mission_type)
                    print("done")
                    with open(file_name, 'w') as out_file:
                        out_file.writelines(csv)
                    break