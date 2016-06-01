#!/usr/bin/python

import sys
import os
import time
import subprocess
import urllib2
import docker
import json
from jinja2 import FileSystemLoader, Environment

FLUENTD_CONF = '/etc/td-agent/conf.d/000_docker.conf'

def get_container_config_native(container_names):
    client = docker.Client(version='auto')
    out = []

    for container_name in container_names:
        try:
            info = client.inspect_container(container_name)
            out.append(dict(
                id = info['Id'],
                name = container_name
            ))
        except:
            pass

    return out

def get_ecs_agent_ip():
    client = docker.Client(version='auto')
    try:
        return client.inspect_container('ecs-agent')['NetworkSettings']['IPAddress']
    except:
        return None

def get_container_config_ecs(ecs_agent_ip, container_names):
    tasks = json.load(urllib2.urlopen('http://%s:51678/v1/tasks' % ecs_agent_ip))['Tasks']
    out = []

    for task in tasks:
        for container in task['Containers']:
            if container['Name'] in container_names:
                out.append(dict(
                    id = container['DockerId'],
                    name = container['Name']
                ))
    return out

def gen_fluentd_conf(config):
    env = Environment(loader = FileSystemLoader('.'))
    template = env.get_template('fluentd.conf.j2')
    out = template.render(containers = config)
    print out
    file(FLUENTD_CONF, 'w').write(out)

def start_fluentd():
    subprocess.call('/usr/sbin/td-agent')
    
def main():
    if not 'CONTAINERS' in os.environ:
        print "Please set the CONTAINERS environment variable."
        return
    
    ecs_agent_ip = get_ecs_agent_ip()

    containers = os.environ['CONTAINERS'].split(',')

    if ecs_agent_ip:
        print "ECS Agent detected, using Agent"
    
    print "Connecting to containers' logs..."
    waiting_shown = False
    while True:
        if ecs_agent_ip:
            config = get_container_config_ecs(ecs_agent_ip, containers)
        else:
            config = get_container_config_native(containers)

        if len(config) < len(containers):
            if not waiting_shown:
                print 'Some containers are missing, waiting for them...'
                waiting_shown = True
        else:
            break

        time.sleep(1)

    gen_fluentd_conf(config)
    start_fluentd()

if __name__ == '__main__':
    main()
