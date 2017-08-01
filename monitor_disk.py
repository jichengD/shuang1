#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
monitor  online server disk if Capacity greater 70% send warning
"""

import subprocess
import commands
import time

def run_cmd(cmd):
    return commands.getstatusoutput(cmd)

def call(cmd):
    args = ['/bin/bash', '-c', cmd]
    subprocess.call(args)

def send_message(message):
    cmd="""curl https://oapi.dingtalk.com/robot/send?access_token=xxxxx \
        -H 'Content-Type: application/json' \
        -d '
          {"msgtype": "text",
            "text": {
                "content": "%s"
             }
          }'""" % message
    call(cmd)

def get_disk_data():
    disk_point = [
        '/',
        '/sf-data1',
        '/sf-data2'
    ]
    disk_rate = {}
    for disk in disk_point:
        cmd = "df -P %s" % disk + " | tail -1 | awk '{print $5 }' | cut -d'%' -f1"
        usage_rate = run_cmd(cmd)[1]
        disk_rate[disk] = usage_rate

    return disk_rate


def monitor():
    print time.ctime()
    cmd = 'hostname'
    hostname = run_cmd(cmd)[1]
    disk_rate = get_disk_data()
    for partition, rate in disk_rate.iteritems():
        rate = int(rate)
        if rate >= 75:
            message = "%s %s partition disk usage over %d%%" % (hostname, partition, rate)
            send_message(message)


if __name__ == "__main__":
    monitor()
