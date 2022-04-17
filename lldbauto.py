import socket
import os
import sys
import re
import time
import threading
import struct


class LLDBAutomation:
    def __init__(self, server_ip, server_port):
        self.ip = server_ip
        self.lldb_server_port = server_port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((server_ip, server_port))
        self.s.send(b"+")
        self.disable_ack()

    def disable_ack(self):
        self.s.send(b"$QStartNoAckMode#b0")
        self.s.recv(1)
        self.s.recv(4096)
        self.s.send(b"+")

    def calc_checksum(self, message):
        sum = 0
        for c in message:
            sum += ord(c)
        sum = sum % 256
        return f"{sum:02x}"

    def send_message(self, message, recvflag=True):
        m = "$" + message + "#" + self.calc_checksum(message)
        self.s.send(m.encode())
        if recvflag:
            result = self.s.recv(4096)
            # ignore $***#hh
            return result[1:-3]

    def attach(self, pid):
        result = self.send_message(f"vAttach;{pid:02x}")
        self.attach_pid = pid

    def cont(self):
        result = self.send_message("c")
        return result

    def readmem(self, address, size):
        result = self.send_message(f"x{address:02x},{size}")
        return result

    # 2:write 3:read 4:access
    def set_watchpoint(self, address, size, _type):
        command = ""
        if _type == "w":
            command = "Z2"
        elif _type == "r":
            command = "Z3"
        elif _type == "a":
            command = "Z4"
        result = self.send_message(f"{command},{address:02x},{size}")
        if result == b"OK":
            return True
        else:
            return False

    def remove_watchpoint(self, address, _type, size):
        command = ""
        if _type == "w":
            command = "z2"
        elif _type == "r":
            command = "z3"
        elif _type == "a":
            command = "z4"
        result = self.send_message(f"{command},{address:02x},{size}")
        if result == b"OK":
            return True
        else:
            return False

    def parse_result(self, result):
        _dict = {}
        for r in result.decode().split(";"):
            if r.find(":") != -1:
                key, value = r.split(":")
                if key == "medata" and key in _dict:
                    if int(value, 16) > int(_dict[key], 16):
                        _dict[key] = value
                else:
                    _dict[key] = value
        return _dict

    def interrupt(self):
        self.send_message("\x03", False)