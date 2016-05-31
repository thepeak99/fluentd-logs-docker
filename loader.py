#!/usr/bin/python

import sys
import os
import glob
import json
import time
import subprocess
from jinja2 import FileSystemLoader, Environment

FLUENTD_CONF = '/etc/td-agent/conf.d/000_docker.conf'

def get_container_config(containers):
    config_files = glob.glob('/var/lib/docker/containers/*/config.v2.json')

    out = []
    
    for config_file in config_files:
        config = json.load(file(config_file))
        if config['Name'][1:] in containers:
            out.append(config)

    return out

def gen_fluentd_conf(config):
    env = Environment(loader = FileSystemLoader('.'))
    template = env.get_template('fluentd.conf.j2')
    out = template.render(containers = config)
    file(FLUENTD_CONF, 'w').write(out)

def start_fluentd():
    subprocess.call('/usr/sbin/td-agent')
    
def main():
    containers = os.environ['CONTAINERS'].split(',')

    print "Connecting to containers' logs..."
    waiting_shown = False
    while True:
        config = get_container_config(containers)

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
