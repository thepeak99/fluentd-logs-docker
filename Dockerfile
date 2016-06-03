FROM thepeak/fluentd

RUN apt-get update && apt-get -y install python python-jinja2 python-pip
RUN pip install docker-py
RUN td-agent-gem install fluent-plugin-parser

ADD loader.py fluentd.conf.j2 /tmp/

WORKDIR /tmp
CMD ["/usr/bin/python", "-u", "loader.py"]
