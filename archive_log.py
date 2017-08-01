#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
    Author :  zhang.shuang@.com
    Date : 2017-07-26
    Desc : Everyday 2.AM tar jdy-log-01  log files
'''
import commands
import subprocess
import datetime
import os
import sys
import re

log_dir='/bascs'
log_types = [
        'php_fpm',
        '_module',
        '_core',
        '_service',
        '_nginx'
        ]

def run_cmd(cmd, mute=False):
    if not mute:
        print cmd
    return commands.getstatusoutput(cmd)

def call(cmd, mute=False):
    if not mute:
        print cmd
    args = ['/bin/bash', '-c', cmd]
    return subprocess.call(args)

def run_cmd_ret(cmd):
    return run_cmd(cmd)[0]


def tar_log_files():

    log_files = [ f for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir,f)) and f.endswith('log') ]

    now = datetime.datetime.now()
    diff = now - datetime.timedelta(days=2)
    log_date = diff.strftime("%Y%m%d")
    for type in log_types:
        log_file = type + '-' + log_date + '.log'
        if log_file in log_files:
            cmd = "cd %s && tar -zcvf %s %s" % (log_dir,log_file + '.tar.gz', log_file)
            ret = run_cmd_ret(cmd)
            if ret == 0:
                rm_cmd = "rm -rf %s" % os.path.join(log_dir,log_file)
                run_cmd(rm_cmd)
        else:
            continue


if __name__ == '__main__':
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' begin tar logfile......'
    tar_log_files()
