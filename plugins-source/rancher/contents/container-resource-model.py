"""
Get running containers
"""
import json
import os
import re
from collections import OrderedDict


import requests
from requests.auth import HTTPBasicAuth

# todo: optional one container per service?
# todo: ignore sidekicks?

api_base_url = os.environ.get('RD_CONFIG_CATTLE_CONFIG_URL')
api_access_key = os.environ.get('RD_CONFIG_CATTLE_ACCESS_KEY')
api_secret_key = os.environ.get('RD_CONFIG_CATTLE_SECRET_KEY')
api_auth = HTTPBasicAuth(api_access_key, api_secret_key)

# plugin config
environment_ids = os.environ.get('RD_CONFIG_ENVIRONMENTS_IDS', '').lower().split(',')
stack_filter = os.environ.get('RD_CONFIG_STACK_FILTER', '').lower()
limit_one_container = (os.environ.get('RD_CONFIG_LIMIT_ONE_CONTAINER', 'false') == 'true')


nodes = OrderedDict()
for environment_id in environment_ids:
    if len(environment_id) == 0:
        raise Exception("Environment ID is missing!")


    #get rancher environment name
    api_url_environment = '{}/projects/{}'.format(api_base_url, environment_id)
    api_res_environment = requests.get(api_url_environment, auth=api_auth).json()
    if not 'name' in api_res_environment:
        raise Exception("No data returned from Rancher API while retriving environment name")
    environment_name = api_res_environment['name']


    api_url_containers = '{}/projects/{}/containers'.format(api_base_url, environment_id)
    api_res_containers = requests.get(api_url_containers, auth=api_auth).json()
    if not 'data' in api_res_containers:
        raise Exception("No data returned from Rancher API")
    api_res_list = api_res_containers['data']

    # dealing with paginated results
    while api_res_containers['pagination']['next']:
        api_res_containers = requests.get(api_res_containers['pagination']['next'], auth=api_auth).json()
        if not 'data' in api_res_containers:
            raise Exception("No data returned from Rancher API")
        api_res_list += api_res_containers['data']
        #pass

    # sort containers by name
    sorted_containers = sorted(api_res_list, key=lambda k: k['name'])

    seen_services = []
    for container in sorted_containers:
        node = OrderedDict()
        node['id'] = container['id']
        node['file-copier'] = 'rancher-filecopy'
        node['node-executor'] = 'rancher-executor'
        node['type'] = container['kind']
        node['state'] = container['state']
        node['environment_id'] = container['accountId']
        node['environment_name'] = environment_name
        node['rancher_url'] =  api_base_url
        node['nodename'] = environment_name + '_' + container['name']
        node['image'] = container['imageUuid']
        node['tty'] = bool(container['tty'])
        node['start_once'] = False
        node['hostname'] = '-'  # todo: shouldn't need this?
        # print(json.dumps(container, indent=2))

        # skip rancher network agents
        if 'io.rancher.container.system' in container['labels'] and container['labels']['io.rancher.container.system'] == 'NetworkAgent':
            continue

        # fetch additional labels
        if 'io.rancher.stack.name' in container['labels']:
            node['stack'] = container['labels']['io.rancher.stack.name']

        if 'io.rancher.stack_service.name' in container['labels']:
            node['stack_service'] = container['labels']['io.rancher.stack_service.name']
            if limit_one_container:
                if node['stack_service'] in seen_services:
                    continue
                else:
                    seen_services.append(node['stack_service'])

        if 'io.rancher.container.start_once' in container['labels']:
            node['start_once'] = (container['labels']['io.rancher.container.start_once'].lower() == 'true')

        if len(stack_filter) > 0:
            if 'stack' not in node or not re.search(stack_filter, node['stack'].lower()):
                continue

        nodes[node['nodename']] = node

print json.dumps(nodes, indent=2)
