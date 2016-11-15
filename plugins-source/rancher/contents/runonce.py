from requests.auth import HTTPBasicAuth
import websocket
import requests
import base64
import time
import json
import os
import re
import logging

class ErrorLogger(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        raise Exception (msg)

logger = logging.getLogger('websocket')
logger.setLevel(logging.ERROR)
logger.addHandler(ErrorLogger())

# todo: remove this when rundeck bug is resolved
cattle_config = json.load(open("/rancher-auth-workaround.json"))
api_base_url = cattle_config['host'] # os.environ['CATTLE_CONFIG_URL']
api_access_key = cattle_config['access_key'] #  os.environ['CATTLE_ACCESS_KEY']
api_secret_key = cattle_config['secret_key'] #  os.environ['CATTLE_SECRET_KEY']

node_id = os.environ.get('RD_NODE_ID', '')
if len(node_id) == 0:
    raise Exception("Can't run, node ID is not set!")

# todo: is run-once service?
# todo: is tty disabled?

# tell the service to start before attaching log listener
# api_url_start = "{}/containers/{}?action=start".format(api_base_url, node_id)
# api_res_start = requests.post(api_url_start, auth=HTTPBasicAuth(api_access_key, api_secret_key), json=api_data)
# api_res_start_json = api_res_start.json()
# print(api_res_start_json)
#
# print("---------------------------------------------------------------------")

# if api_res_start.status_code != 200:
#     raise Exception("Can't start service, code \"{} ({})\"!".format(api_res_start_json['code'], api_res_start_json['status']))

print("===============================================")

def events_on_error(ws, error):
    print("### err ###")
    print error

def events_on_close(ws):
    print "### closed ###"

def events_on_open(ws):
    print("### opened ###")

def events_on_message(ws, message):
    json_message = json.loads(message)
    if "resourceId" not in json_message or json_message["resourceId"] != node_id:
        return
    node_state = json_message["data"]["resource"]["state"]
    print(node_state)
    if node_state == "running":
        ws.close()
    # print(json.dumps(json_message, indent=2))

print("Listening...")


# todo: http?
ws_base_url = api_base_url.replace("https", "wss")

# todo: environment ID?
# ws_url_events = "{}/projects/1a81/subscribe?eventNames=resource.change".format(ws_base_url)
# ws_events = websocket.WebSocketApp(ws_url_events,
#     on_open = events_on_open,
#     on_message = events_on_message,
#     on_error = events_on_error,
#     on_close = events_on_close,
#     header = {'Authorization': "Basic {}".format(base64.b64encode("{}:{}".format(api_access_key, api_secret_key)))})
# ws_events.run_forever()

print("#######################################################################")


# setup websocket for reading log output
api_data_logs = {
    "follow": True,
    "lines": 100
}
api_url_logs = "{}/containers/{}?action=logs".format(api_base_url, node_id)
api_res_logs = requests.post(api_url_logs, auth=HTTPBasicAuth(api_access_key, api_secret_key), json=api_data_logs)
api_res_logs_json = api_res_logs.json()
# print(api_res_logs_json)
#
if api_res_logs.status_code != 200:
    raise Exception("Can't create log listener, code \"{} ({})\"!".format(api_res_logs_json['code'], api_res_logs_json['status']))

def logs_on_error(ws, error):
    print("### logs err ###")
    print(error)
    ws.close()

def logs_on_close(ws):
    print "### logs closed ###"

def logs_on_open(ws):
    print("### logs opened ###")

def logs_on_message(ws, message):
    msg_match = re.match('^(\d*) (.*?Z)X (.*)$', message)
    if not msg_match:
        raise Exception("Failed to read log format, regex does not match!")
    print("{} - {}".format(msg_match.group(1), msg_match.group(2)))

# attach to log listener websocket
ws_url_logs = "{}?token={}".format(api_res_logs_json['url'], api_res_logs_json['token'])
ws_logs = websocket.WebSocketApp(ws_url_logs,
    on_open = logs_on_open,
    on_message = logs_on_message,
    on_error = logs_on_error,
    on_close = logs_on_close,
    header = {'Authorization': "Basic {}".format(base64.b64encode("{}:{}".format(api_access_key, api_secret_key)))})
ws_logs.run_forever()

print("=== DONE ===")
# print(base64.b64decode(ws_res).strip())
