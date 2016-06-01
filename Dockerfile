FROM thepeak/fluentd

RUN apt-get update && apt-get -y install python python-jinja2 python-docker

ADD loader.py fluentd.conf.j2 /tmp/

WORKDIR /tmp
CMD ["/usr/bin/python", "-u", "loader.py"]
