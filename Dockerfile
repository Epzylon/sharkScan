#Dockerfile for SharkScan app
FROM alpine
EXPOSE 8080
RUN mkdir /app
RUN mkdir -p /data/db
WORKDIR /app
RUN apk add --no-cache python3 python3-dev gcc libxml2-dev libxslt-dev libc-dev mongodb nmap
RUN /usr/bin/python3 -m ensurepip && rm -r /usr/lib/python*/ensurepip
RUN /usr/bin/pip3 install --upgrade pip setuptools && if [ ! -e /usr/bin/pip ];then ln -s pip3 /usr/bin/pip ; fi; if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && rm -r /root/.cache
RUN pip install lxml pymongo bottle
COPY . /app
ENTRYPOINT /app/run.sh
