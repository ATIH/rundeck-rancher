"""
execute command in container
"""

#import StringIO
import base64
import hashlib
import os
import requests
import websocket
#import re
#pylint: disable=W0401
from _containers_shared import *

working_dir = '/tmp'
leadingrubbish = 8
rundeck_retry_attempt = int(os.environ.get('RD_OPTION_RETRY_ATTEMPT', 5))
rundeck_retry_interval = int(os.environ.get('RD_OPTION_RETRY_INTERVAL', 5))


#need to create a nice class instead of this ugly global var
data_recv = None


def request_token(api_data):
    """
    request token to run command through rancher
    """
    api_url = "{}/containers/{}?action=execute".format(api_base_url, node_id)
    api_res = requests.post(api_url, auth=api_auth, json=api_data)
    api_res_json = api_res.json()
    # log(json.dumps(api_res_json, indent=2))
    if not api_res.status_code < 300:
        raise Exception("Failed to create 'execute script' socket token: API error, code \"{} ({})\"!".format(api_res_json['code'], api_res_json['status']))

    return api_res_json

def on_message(ws, message):
    global data_recv
    data_recv += base64.b64decode(message)

def use_token(token, wait_for_data=False):
    """
    use token
    """

    global data_recv

    #http://docs.rancher.com/rancher/v1.4/en/api/v1/
    ws_url_execute = "{}?token={}".format(token['url'], token['token'])

    if wait_for_data:
        data_recv = ''
        ws_exec = websocket.WebSocketApp(ws_url_execute,
                                        on_message = on_message)
                                        #on_error = on_error,
                                        #on_close = on_close)
        ws_exec.run_forever()

        #https://github.com/rancher/rancher/issues/8078
        data_recv = data_recv[leadingrubbish:]

    else:
        ws_exec = websocket.create_connection(ws_url_execute)
        ws_exec.close()

    return data_recv

def run_command(wait_for_data=False):

    api_data = {
        "attachStdin": False,
        "attachStdout": True,
        "command": [
            "/bin/sh",
            "-c",
            'echo $$ > {working_dir}/{rundeck_job_exec_id}.pid; \
            date -u +%Y-%m-%dT%H:%M:%SZ > {working_dir}/{rundeck_job_exec_id}.out; \
            echo -n "killed" > {working_dir}/{rundeck_job_exec_id}.status; \
            {{ {bash_script} 2>&1 >> {working_dir}/{rundeck_job_exec_id}.out && echo -n "$?" >{working_dir}/{rundeck_job_exec_id}.status || echo -n "$?" >{working_dir}/{rundeck_job_exec_id}.status; }} | while read line;do echo "ERROR - $line" >> {working_dir}/{rundeck_job_exec_id}.out ;done'
            #nohup {bash_script} 2> >(sed "s/^/ERROR - /g" >&2) >> {working_dir}/{rundeck_job_exec_id}.out; echo $? > {working_dir}/{rundeck_job_exec_id}.status'
            #nohup {bash_script} >> {working_dir}/{rundeck_job_exec_id}.out 2>> {working_dir}/{rundeck_job_exec_id}.err'
            .format(rundeck_job_exec_id=rundeck_job_exec_id, bash_script=bash_script, working_dir=working_dir)
        ],
        "tty": False
    }

    return use_token(request_token(api_data), wait_for_data)

@retry(attempts=rundeck_retry_attempt, interval=rundeck_retry_interval)
def check_pid():
    api_data = {
        "attachStdin": False,
        "attachStdout": True,
        "command": [
            "/bin/sh",
            "-c",
            '/bin/kill -0 $(cat {working_dir}/{rundeck_job_exec_id}.pid) > /dev/null 2>&1; echo -n "$?"'

            .format(rundeck_job_exec_id=rundeck_job_exec_id, working_dir=working_dir)
        ],
        "tty": False
    }

    try:
        pid_check_result = use_token(request_token(api_data), wait_for_data=True)
    except ValueError:
        log("[ W ] Failed to read PID state:")
        pid_check_result = -1
    if pid_check_result == '0':
        raise Exception(
            "Process have not yet stopped "
            "in container (PID state {})".format(pid_check_result))

def get_log():
    api_data = {
        "attachStdin": False,
        "attachStdout": True,
        "command": [
            "cat",
            "{working_dir}/{rundeck_job_exec_id}.out"
            .format(rundeck_job_exec_id=rundeck_job_exec_id, working_dir=working_dir)
        ],
        "tty": False
    }

    return use_token(request_token(api_data), True)

def get_status():
    api_data = {
        "attachStdin": False,
        "attachStdout": True,
        "command": [
            "cat",
            "{working_dir}/{rundeck_job_exec_id}.status"
            .format(rundeck_job_exec_id=rundeck_job_exec_id, working_dir=working_dir)
        ],
        "tty": False
    }

    status_code = use_token(request_token(api_data), True)

    return int (status_code)


log("-Starting job")

#print os.environ

# Read rundeck values
bash_script = os.environ.get('RD_EXEC_COMMAND', '')
bash_script = bash_script.strip().encode("string_escape").replace('"', '\\\"')
if len(bash_script) == 0:
    raise Exception("Can't run, command is empty!")


# check container is running
container_info_res = get_container_information()
if container_info_res['state'] != 'running':
    raise Exception("Invalid container state, must be set to 'running'!")



# create an unique ID for this job execution
rundeck_project = os.environ.get('RD_RUNDECK_PROJECT', '')
check_os_env(rundeck_project, 'No RD_RUNDECK_PROJECT defined')

rundeck_exec_id = os.environ.get('RD_JOB_EXECID', '')
check_os_env(rundeck_exec_id, 'No RD_JOB_EXECID defined')

#rundeck_retry_interval = os.environ.get('RD_JOB_RETRYINTERVAL', '')
#check_os_env(rundeck_retry_interval, 'No RD_JOB_RETRYINTERVAL defined')

#rundeck_retry_attempt = os.environ.get('RD_JOB_RETRYATTEMPT', '')
#check_os_env(rundeck_retry_attempt, 'No RD_JOB_RETRYATTEMPT defined')

m = hashlib.md5()
m.update(bash_script)
bash_script_md5 = m.hexdigest()
rundeck_job_exec_id = "rundeck_{}_{}_{}_{}".format(rundeck_project, rundeck_exec_id, rundeck_retry_attempt, bash_script_md5)

#rundeck_job_exec_id = 'super'

log("-Running your command : " +  rundeck_job_exec_id)
run_command()

log("\n-Waiting for the end...")
check_pid()

log("\n-Gathering logs...")
print get_log()

log("\n-Getting status...")
return_code = get_status()
print return_code

log("\n-finish")

sys.exit(return_code)
