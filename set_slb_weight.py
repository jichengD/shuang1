#!/usr/bin/env python
# -*- coding:utf-8 -*-

from aliyunsdkcore.client import AcsClient
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancersRequest, DescribeLoadBalancerAttributeRequest, SetBackendServersRequest
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
import json, sys, argparse
from collections import defaultdict

class Slb:

    def __init__(self):
        self.client = AcsClient('', '', 'cn-beijing')
        self.lbs_config = [
            'abc',
            '123'
        ]

    # request aliyun api
    def _request(self, request):

        response = self.client.do_action_with_exception(request)
        result = json.loads(response)
        return result


    # get  all slb
    def get__lbids(self):

        request = DescribeLoadBalancersRequest.DescribeLoadBalancersRequest()
        result = self._request(request)
        slbs = result['LoadBalancers']['LoadBalancer']

        #print json.dumps(slbs,sort_keys=True,indent=4, separators=(',', ': '))
        lbid = []
        # get www..com admin..com LoadBalancerId
        for slb in slbs:
            if slb['LoadBalancerName'] in self.lbs_config:
                lbid.append(slb['LoadBalancerId'])

        return lbid


    # get lb attr by lbid
    def get_lb_attr(self, lbids):

        instanceIds = defaultdict(set)
        for lbid in lbids:
            request = DescribeLoadBalancerAttributeRequest.DescribeLoadBalancerAttributeRequest()
            request.set_LoadBalancerId(lbid)
            result = self._request(request)
            #print json.dumps(result,sort_keys=True,indent=4, separators=(',', ': '))
            for server in result['BackendServers']['BackendServer']:
                instanceIds[lbid].add(server['ServerId'])

        return instanceIds


    # get ecs by instance ids
    def get_ecs_instances_by_ids(self, instanceIds):

        instanceIds = json.dumps(instanceIds)
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_InstanceIds(instanceIds)
        result = self._request(request)

        #print json.dumps(result,sort_keys=True,indent=4, separators=(',', ': '))
        ecs_list = {}
        for instance in result['Instances']['Instance']:
            ecs_list[instance['InstanceName']] = instance['InstanceId']

        return ecs_list

    # set backend server weight
    def set_lb_weight(self, lbid, instanceId, weight):

        servers = [{'ServerId' : instanceId, 'Weight' : weight}]
        servers = json.dumps(servers)
        request = SetBackendServersRequest.SetBackendServersRequest();
        request.set_LoadBalancerId(lbid)
        request.set_BackendServers(servers)
        result = self._request(request)

        print json.dumps(result,sort_keys=True,indent=4, separators=(',', ': '))


    def get_ecs_list(self):

        lbids = self.get__lbids()
        instanceIds = self.get_lb_attr(lbids)

        id_sets = set()
        for val in instanceIds.values():
            id_sets.update(val)

        id_list = list(id_sets)
        ecs_list = slb.get_ecs_instances_by_ids(id_list)

        return instanceIds, ecs_list




    def check_host(self,instanceid_list, ecs_list, hostname):

        if hostname not in ecs_list:
            print "server not found"
            sys.exit()

        instanceId = ecs_list[hostname]
        lbid = ''

        for slb, instanceIds in instanceid_list.iteritems():
            if instanceId in instanceIds:
                lbid = slb

        if lbid == '':
            print "slb id not found"
            sys.exit()

        return lbid, instanceId


    def remove_backend_server(self, hostname):

        instanceid_list, ecs_list = self.get_ecs_list()
        lbid, instanceId = self.check_host(instanceid_list, ecs_list, hostname)
        self.set_lb_weight(lbid, instanceId, 0)


    def online_backend_server(self, hostname):

        instanceid_list, ecs_list = self.get_ecs_list()
        lbid, instanceId = self.check_host(instanceid_list, ecs_list, hostname)
        self.set_lb_weight(lbid, instanceId, 100)


if __name__ == "__main__" :

    parser = argparse.ArgumentParser()

    parser.add_argument('--remove_backend_server', metavar=('hostname'), nargs=1, required=False)
    parser.add_argument('--online_backend_server', metavar=('hostname'), nargs=1, required=False)

    args = parser.parse_args()

    slb = Slb()

    if args.remove_backend_server:
        slb.remove_backend_server(args.remove_backend_server[0])

    if args.online_backend_server:
        slb.online_backend_server(args.online_backend_server[0])

