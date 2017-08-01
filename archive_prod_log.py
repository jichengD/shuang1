#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
    Author :  zhang.shuang@.com
    Date : 2017-07-26
    Desc : Everyday 2.AM tar jdy production logfiles
'''
import commands
import subprocess
import datetime
import os
import sys
import re

log_dir='xxxxxxxxx'
log_types = {
        '-module' : ['laravel_info-','laravel_error-','wechat_'],
        '-core' : ['lumen-'],
        '-service' : ['lumen-']
        }

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
    host = os.uname()[1]
    for type, val in log_types.iteritems():
        real_log_dir = os.path.join(log_dir,type,'logs')
        log_files = [ f for f in os.listdir(real_log_dir) if os.path.isfile(os.path.join(real_log_dir,f)) and f.endswith('log') ]

        now = datetime.datetime.now()
        diff = now - datetime.timedelta(days=1)
        log_date = diff.strftime("%Y-%m-%d")
        for log_prefix in val:
            log_file = log_prefix + log_date + '.log'
            if log_file in log_files:
                tar_file = log_file + '.tar.gz'
                cmd = "cd %s && sudo tar -zcvf %s %s" % (real_log_dir,tar_file, log_file)
                ret = run_cmd_ret(cmd)
                if ret == 0:
                    rm_cmd = "sudo rm -rf %s" % os.path.join(real_log_dir,log_file)
                    run_cmd(rm_cmd)
            else:
                continue


if __name__ == '__main__':
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' begin tar and rsync logfile......'
    tar_log_files()
