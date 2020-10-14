#!/usr/bin/env python3

import os
import sys
import time
import datetime
import logging
import socket

LOG = logging.getLogger('test_client')
LOG.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGSTREAM = logging.StreamHandler(sys.stdout)
LOGSTREAM.setFormatter(FORMATTER)
LOG.addHandler(LOGSTREAM)

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001


def initialize():
    global SERVER_HOST, SERVER_PORT
    SERVER_HOST = os.getenv('SERVER_HOST', '127.0.0.1')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '5001'))
    if len(sys.argv) == 3:
        SERVER_HOST = sys.argv[1]
        SERVER_PORT = int(sys.argv[2])


def return_gateway_ip(data):
    return data.split('>')[1].split(':')[0].strip()


def connect_and_report(host=None, port=None):
    if not host:
        host = SERVER_HOST
    if not port:
        port = SERVER_PORT
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))
    return client.recv(256).decode('utf8').strip()


def main():
    data = connect_and_report()
    LOG.info('client received: %s', data)
    LOG.info('gateway ip: %s', return_gateway_ip(data))


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
        sys.exit(1)
