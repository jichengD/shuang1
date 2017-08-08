#!/bin/bash
#jdy app request log
#Author: zhang.shuang@.com

set -e

function run_cmd() {                                                                                                                                                                                                                           
    local t=`date`                                                                                                                                                                                                                              
    echo "$t: $1"                                                                                                                                                                                                                              
    eval $1                                                                                                                                                                                                                                    
}

yest=$(date --date="1 day ago" +"%Y%m%d")
log_file="/xxxxxx/_module-${yest}.log"

app_log_file="/tmp/_app-${yest}.log"

cmd="cat $log_file | grep unique | grep 'app4.0+ auth' | grep unique |   awk '! /token/ || /theFirst/ {print \$0}' >> $app_log_file"

if [ -f $log_file ];then
    run_cmd "$cmd"
fi

