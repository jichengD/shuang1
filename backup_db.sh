#!/bin/sh
#desc : every 2 hours full backup jdy databases
#date : 2016-09-21
#author : zhang.shuang@.com

Path_backup='xxxxx'
Path_dump='xxxxx'

#Date
file_name=`date +%Y%m%d%H%M`
ErrorLog="xxxxxx"

#parameter
checkrun()
{

result="$?"

if [ $result -eq 0 ]
then
  :
else
  echo "Error $1 has happened at $file_name" >> $ErrorLog
  exit 10
fi
}

#del old file
find $Path_backup -name "*.zip" -a -mtime +30 -exec rm {} -f \;
checkrun find_rm_1

$Path_dump   --add-drop-table -uxxxx -pxxxx -hxxxxx --set-gtid-purged=OFF _core_db > $Path_backup/_core_db_$file_name.sql
$Path_dump   --add-drop-table -uxxxx -pxxxx -hxxxxx --ignore-table=_module_db.module_credit_merge --set-gtid-purged=OFF _module_db > $Path_backup/_module_db_$file_name.sql
$Path_dump   --add-drop-table -uxxxx -pxxxx -hxxxxx --set-gtid-purged=OFF _service_db > $Path_backup/_service_db_$file_name.sql

checkrun mysqldump


cd $Path_backup/
zip _core_db_$file_name.sql.zip _core_db_$file_name.sql
zip _module_db_$file_name.sql.zip _module_db_$file_name.sql
zip _service_db_$file_name.sql.zip _service_db_$file_name.sql
checkrun zip


rm -f _core_db_$file_name.sql
rm -f _module_db_$file_name.sql
rm -f _service_db_$file_name.sql

file_name2=`date +%Y%m%d%H%M`
echo $file_name2 > /tmp/backup_end_time.txt
