#!/bin/bash
# production online and update database
#Author: zhang.shuang@.com

set -e

function run_cmd() {                                                                                                                                                                                                                           
    local t=`date`                                                                                                                                                                                                                              
    echo "$t: $1"                                                                                                                                                                                                                              
    eval $1                                                                                                                                                                                                                                    
}

function list_contains() {

    local var="$1"
    local str="$2"
    local val

    eval "val=\" \${$var} \""
    [ "${val%% $str *}" != "$val" ]
}

host_code_root_dir=afdsdf


host_code_core_dir=$host_code_root_dir/-core
host_code_module_dir=$host_code_root_dir/-module
host_code_static_dir=fdfsdf
host_code_service_dir=$host_code_root_dir/-service

_web001=xxxx
_web002=xxxxx
_web003=xxxxx

_static=xxxx

_user=abc

_ssh_port=afdsfs

function new_egg(){
    pull_code
    #update_database
}


function pull_code() {

    local vendor_dir=vendor
    for web_server in $_web001 $_web002 $_web003
    do
        
        for dir in $host_code_core_dir/$vendor_dir $host_code_module_dir/$vendor_dir $host_code_service_dir/$vendor_dir $host_code_service_dir $host_code_core_dir $host_code_module_dir
        do
            run_cmd "ssh -A -p $_ssh_port $_user@$web_server 'cd $dir && git pull'"
            if [ "$?" != "0" ];then
                echo "pull $web_server $dir code failed"
                exit 1
            else
                echo "pull $web_server $dir code success"
            fi
        done
    done

    for dir in $host_code_static_dir
    do
        run_cmd "ssh -A -p $_ssh_port $_user@$_static 'cd $dir && git pull'"
    done
}

function update_database(){
    
    local php_cmd=/opt/lampp/bin/php
    for dir in $host_code_service_dir $host_code_core_dir $host_code_module_dir
    do
        run_cmd "ssh -A -p $_ssh_port $_user@$_web001 'cd $dir && $php_cmd artisan migrate --force'"

        if [ "$?" != "0" ];then
            echo "update $dir database failed"
            exit 1
        else
            echo "update $dir database success"
         fi
    done
    
}

action=${1:-help}
if [ $# -lt 1 ]; then
    echo "Usage sh $0 help";
    exit 1
fi

function help() {

    cat <<-EOF

        Usage: mamanger.sh [options]

                Valid options are:
                new_egg
                pull_code
                update_database

EOF
}

ALL_COMMANDS="new_egg pull_code update_database"
list_contains ALL_COMMANDS "$action" || action=help
$action "$@"



