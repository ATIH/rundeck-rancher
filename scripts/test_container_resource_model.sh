#!/bin/bash
CD_FAILED=1


GIT_ROOT='/home/damien/git/rundeck/plugins/rundeck-rancher'

export RD_NODE_RANCHER_URL="${RD_NODE_RANCHER_URL:=myrancher.nop}"
export RD_CONFIG_CATTLE_ACCESS_KEY="${RD_CONFIG_CATTLE_ACCESS_KEY:=mykey}"
export RD_CONFIG_CATTLE_SECRET_KEY="${RD_CONFIG_CATTLE_SECRET_KEY:=mysecret}"
export RD_CONFIG_STACK_FILTER="${RD_CONFIG_STACK_FILTER:=demostack}"
export RD_CONFIG_ENVIRONMENTS_IDS='1a11011,1a11090,1a22082'
cd $GIT_ROOT || exit $CD_FAILED
python ./plugins-source/rancher/contents/container_resource_model.py
