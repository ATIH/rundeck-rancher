<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


DONT US ME. I'M DEPRECATED.
IT'S A BAD WAY TO DO WHAT YOU WANT TO.

**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Rundeck for Rancher](#rundeck-for-rancher)
  - [Getting started](#getting-started)
    - [Requirements](#requirements)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Use it](#use-it)
      - [Commande execution](#commande-execution)
  - [Notes :](#notes-)
    - [General](#general)
    - [Rancher container file copier](#rancher-container-file-copier)
    - [Rancher trigger run-once container](#rancher-trigger-run-once-container)
  - [Links:](#links)
  - [Merge requests](#merge-requests)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Rundeck for Rancher

This plugin is based on ["kallqvist/rundeck-rancher" ](https://github.com/kallqvist/rundeck-rancher) work.

The goal here is to create a rundeck plugin able to :
- [x] Run with rundeck directly (running, or not, in a container).
- [x] Using Rancher Rest-API and websockets to execute bash commands in already running containers (as returned by ResourceModelSource plugin).
- [x] Run command into container even if tty is activated.
- [x] Connect a job to several rancher environments
- [ ] Trigger a "start-once" container
- [ ] Send/Run file/script into container

## Getting started
### Requirements
- Tested on Rundeck 2.6.11-1
- Config and API keys specific to your Rancher installation.
- `/bin/sh` need to be present in the container.
- Python 2
- Some python librairies installed on your rundeck server :
 - websocket-client (>=0.37.0)
 - requests (>=2.12.4)
 - python-dateutil (>=2.5.3)<br>
(something like : apt-get install python-websocket python-requests python-dateutil)

### Installation
- Choose your release and download the `rancher-plugin.zip`
- Place it in `$RDECK_BASE/libext/`.

or build it (bash & zip needed)

- Clone this reposiroty
- Run `scripts/build-all.sh` (need `zip` in your PATH)
- Copy the file `target/rancher-plugin.zip` to your rundeck serveur at `$RDECK_BASE/libext/`.


### Configuration
- add a new `Resource Model Source` in your projet configuration : <br>
(You need to adapte the source number "1" according to your project) configuration

 - `resources.source.1.type=rancher-resources`<br>
 The rancher-plugin resources model definition.

 - `resources.source.1.config.cattle_access_key=0123456789AABBCCDDEE`<br>
 Your acces key to connect to the rancher API

 - `resources.source.1.config.cattle_config_url=https\://myrancher.home/v1`<br>
 Mind the "\" before ":"<br>
 You can use API v1 or v2-beta

 - `resources.source.1.config.cattle_secret_key=azertyuiopqsdfghjklmwxcvbn123456798000`<br>
 Your secret key to connect to the rancher API

 - `resources.source.1.config.environments_ids=1a11029,1a11070,1a11082`<br>
 Your different environments IDs to search in (comma separated).

 - `resources.source.1.config.limit_one_container=false`<br>
 Only retrieve one container from earch environment ID.

 - `resources.source.1.config.stack_filter=my_super_stack`<br>
 Restrict containers discovery to a specific stack.



- Configure a new `Node Executor` method : <br>
(You need to specify the accound used by the plugin to connect and run command through rancher's API)
 - `project.plugin.NodeExecutor.rancher-executor.cattle_access_key=0987654321EECCDDBBAA`<br>
 Your acces key to connect to the rancher API. Same or different as the resources source

 - `project.plugin.NodeExecutor.rancher-executor.cattle_secret_key=gAbmufoxW753PktyqKbcs4gjUMfJWRK4YYzwXLso`<br>
 Your secret key to connect to the rancher API. Same or different as the resources source

### Use it
#### Commande execution
- Add a step `Command` to your workflow.
- Specify you command as usual (ex: /bin/ls /tmp)

- It's something good to filter nodes with properties like : `type: container`, `state: running` and even `environment_name: something`

- if needed, you can add 2 options to your job definition :
 - retry_attemp (default 5)<br>
 How many times rundeck should check if your command have finished.

 - retry_interval (default 30)<br>
 How long should rundeck wait between each check (in second).

Your command will be sent to the container, when rundeck will check until it finishes.

At the end, you will get a log containing all stdout and stderr at once.<br>
All stderr intries are prefixed with "ERROR - ".

The exit code of your command will be send to rundeck.

## Notes :
### General
- Providers for "node-executor" and "file-copier" are stored in the node attributes.

### Rancher container file copier
- Not tested, do not use it.

### Rancher trigger run-once container
- Not tested, do not use it.

## Links:
- [Rundeck](http://rundeck.org/)
- [Rancher](http://rancher.com/rancher/)

## Merge requests
- Do not hesitate to contribute.
