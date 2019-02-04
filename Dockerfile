FROM python:3.7

MAINTAINER Max Meinhold <mxmeinhold@gmail.com>

ENV APP_ROOT=/opt/app-root

RUN python3 -m venv /opt/app-root

ADD requirements.txt /opt/app-root/

WORKDIR /opt/app-root

RUN . bin/activate && pip install -r requirements.txt

ADD . /opt/app-root

RUN chown -R 1001:0 /opt/app-root 

USER 1001

CMD ["./start.sh"]
