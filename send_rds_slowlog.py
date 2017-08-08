#!/usr/bin/env python
# -*- coding:utf-8 -*-
from aliyunsdkcore.client import AcsClient
from aliyunsdkrds.request.v20140815 import DescribeDBInstancesRequest, DescribeSlowLogRecordsRequest, DescribeDBInstanceAttributeRequest
import json, sys, time, datetime, csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib, os, codecs, re

from email.header import Header

class Slowlog:

    '''
    Author : zhangshuang
    Email : zhang.shuang@.com
    Desc : Every 3:00 PM send  RDS slowlog by email
    '''

    def __init__(self):

        self.client = AcsClient('', '', 'cn-beijing')

        self.email_config = {
            'smtp_server' : 'aliyu@mail.com:465',
            'password' : 'asfs',
            'from_addr': 'abc@163.com',
        }

        #to_addrs = 'zhang.shuang@.com'
        self.to_addrs = [
            'abc@163.com',
        ]

    # send email
    def send_email(self, subject, content, attatchs = None):

        from_addr = self.email_config['from_addr']
        password = self.email_config['password']

        ##创建一个带附件的实例
        msg = MIMEMultipart()
        # 邮件正文内容
        msg.attach(MIMEText(content, 'plain', 'utf-8'))

        msg['From'] = from_addr
        msg['To'] = ','.join(self.to_addrs)
        msg['Subject'] = Header(subject, 'utf-8').encode()

        for attatch in attatchs:
            # 构造附件1，传送当前目录下的 select.sql.py 文件
            att = MIMEText(open(attatch, 'rb').read(), 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'
            filename = os.path.basename(attatch)

            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            att["Content-Disposition"] = 'attachment; filename="'+ filename + '"'
            msg.attach(att)

        try:
            server = smtplib.SMTP_SSL(self.email_config['smtp_server'])
            server.login(from_addr, password)
            #server.set_debuglevel(1)
            server.sendmail(from_addr, self.to_addrs, msg.as_string())
            server.quit()
            print "send email success ..."
        except Exception as e:
            print e


    # request aliyun api
    def _request(self, request):
        response = self.client.do_action_with_exception(request)
        result = json.loads(response)
        return result


    # get  all slb
    def get_rds_list(self):

        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        result = self._request(request)

        instance_list = []
        for item in result['Items']['DBInstance']:
            instance_list.append(item['DBInstanceId'])

        #print json.dumps(result,sort_keys=True,indent=4, separators=(',', ': '))
        return instance_list


    def get_rds_detail_by_ids(self, instance_list):

        id_str = ','.join(instance_list)
        request = DescribeDBInstanceAttributeRequest.DescribeDBInstanceAttributeRequest()
        request.set_DBInstanceId(id_str)

        result = self._request(request)

        desc_key = 'DBInstanceDescription'
        pfb_db_list = [
            '-master',
            '-redash-slave',
            #'brcb-prod-master'
        ]

        id_desc_list = {}

        for item in result['Items']['DBInstanceAttribute']:
            if desc_key not in item or item[desc_key] not in pfb_db_list:
                continue
            else:
                id_desc_list[item[desc_key]] = item['DBInstanceId']

        return id_desc_list
        #print json.dumps(result,sort_keys=True,indent=4, separators=(',', ': '))



    # get slowlog by instanceid
    def send_rds_slowlog_by_id(self, id_desc_list):

        log_path_list = []
        now = datetime.datetime.now()
        diff = now - datetime.timedelta(days=1)
        start_time = diff.strftime("%Y-%m-%dT%H:00Z")
        end_time = now.strftime("%Y-%m-%dT%H:00Z")

        for dbname, dbid in id_desc_list.items():
            request = DescribeSlowLogRecordsRequest.DescribeSlowLogRecordsRequest()
            request.set_DBInstanceId(dbid)
            request.set_PageSize(50)
            request.set_StartTime(start_time)
            request.set_EndTime(end_time)

            result = self._request(request)
            #print json.dumps(result,sort_keys=True,indent=4, separators=(',', ': '))

            if result['TotalRecordCount'] > 0:
                log_path = "/tmp/%s-slowlog.csv" % dbname
                self.save_csv(result['Items']['SQLSlowRecord'], log_path)
                log_path_list.append(log_path)

        if log_path_list:
            self.send_email(u"数据库慢SQL", u"附件为%s ~ %s慢日志，请查收。谢谢！" % (start_time, end_time), log_path_list)


    # save slowlog to csv file
    def save_csv(self, slow_list, log_path):

        with open(log_path, 'wb') as f:
            f.write(codecs.BOM_UTF8)
            fieldnames = ['DBName', 'ExecutionStartTime', 'HostAddress', 'LockTimes', 'ParseRowCounts', 'QueryTimes', 'ReturnRowCounts', 'SQLText']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for record in slow_list:
                sql = record['SQLText'].encode('utf-8')
                record['SQLText'] = re.sub(r'^.*\*\/', "", sql)
                writer.writerow(record)


if __name__ == "__main__" :

    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " get  rds slowlogs begin ....."

    slog = Slowlog()
    instance_list = slog.get_rds_list()
    id_desc_list = slog.get_rds_detail_by_ids(instance_list)
    slog.send_rds_slowlog_by_id(id_desc_list)
    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " send  rds slowlogs end ....."
