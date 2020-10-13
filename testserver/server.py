#!/usr/bin/env python3

import os
import sys
import logging
import time
import datetime
import socket
import fcntl
import struct
import threading

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001
SERVER_ETH0_IP = ''

LOG = logging.getLogger('test_server')
LOG.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGSTREAM = logging.StreamHandler(sys.stdout)
LOGSTREAM.setFormatter(FORMATTER)
LOG.addHandler(LOGSTREAM)


def get_interface_ip(interface):
    return os.popen("ip addr show %s" % interface).read().split("inet ")[1].split("/")[0]

def get_default_gw_interface():
    return os.popen("ip r|grep default|grep -v dhcp|cut -d' ' -f5").read()


def initialize():
    global SERVER_HOST, SERVER_PORT, SERVER_ETH0_IP
    SERVER_HOST = os.getenv('SERVER_HOST', '127.0.0.1')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '5001'))
    SERVER_ETH0_IP = get_interface_ip(get_default_gw_interface())


class ClientThread(threading.Thread):

    def __init__(self, conn, ip, port):
        threading.Thread.__init__(self)
        self.conn = conn
        self.ip = ip
        self.port = port
        LOG.debug('accepted connection for %s:%d', ip, port)

    def run(self):
        message = "%s:%s->%s:%s" % (self.ip, self.port,
                                    SERVER_ETH0_IP, SERVER_PORT)
        self.conn.send(message.encode())
        self.conn.close()


def main():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((SERVER_HOST, SERVER_PORT))

    client_threads = []

    while True:
        listener.listen(4)
        (conn, (ip, port)) = listener.accept()
        client_thread = ClientThread(conn, ip, port)
        client_thread.start()
        client_threads.append(client_thread)

    for t in client_threads:
        t.join()


if __name__ == '__main__':
    try:
        START_TIME = time.time()
        LOG.debug('process start time: %s', datetime.datetime.fromtimestamp(
            START_TIME).strftime("%A, %B %d, %Y %I:%M:%S"))
        initialize()
        main()
        STOP_TIME = time.time()
        DURATION = STOP_TIME - START_TIME
        LOG.debug(
            'process end time: %s - ran %s (seconds)',
            datetime.datetime.fromtimestamp(
                STOP_TIME).strftime("%A, %B %d, %Y %I:%M:%S"),
            DURATION
        )
    except Exception as ex:
        LOG.error(ex)
        raise ex
        sys.exit(1)
