#!/bin/bash
CD_FAILED=1


GIT_ROOT="$(git rev-parse --show-toplevel)"

export RD_NODE_RANCHER_URL="${RD_NODE_RANCHER_URL:=myrancher.nop}"
export RD_CONFIG_CATTLE_ACCESS_KEY="${RD_CONFIG_CATTLE_ACCESS_KEY:=mykey}"
export RD_CONFIG_CATTLE_SECRET_KEY="${RD_CONFIG_CATTLE_SECRET_KEY:=mysecret}"
export RD_CONFIG_STACK_FILTER="${RD_CONFIG_STACK_FILTER:=demostack}"

export RD_EXEC_COMMAND='sleep 10; ls /tmp /arazerzer'
export RD_RUNDECK_PROJECT='test_docker'
export RD_JOB_EXECID='1'
export RD_JOB_RETRYATTEMPT=1
export RD_NODE_ENVIRONMENT_ID='1a11011'
export RD_NODE_ID='1i124546'
export RD_OPTION_RETRY_ATTEMPT='10'
export RD_OPTION_RETRY_INTERVAL='5'

export RD_INTERPRETEUR_CMD='/bin/sh'


cd $GIT_ROOT || exit $CD_FAILED
python ./plugins-source/rancher/contents/container_node_executor.py
