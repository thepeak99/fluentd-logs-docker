FROM thepeak/fluentd

RUN apt-get update && apt-get -y install python python-jinja2

ADD loader.py fluentd.conf.j2 /tmp/

ONBUILD ADD fluentd.local.conf /etc/td-agent/

WORKDIR /tmp
CMD ["/usr/bin/python", "-u", "loader.py"]
