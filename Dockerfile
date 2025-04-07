FROM python:3.8-slim-buster AS builder

RUN apt-get update && \
    apt-get install --no-install-recommends -y git

RUN git clone https://github.com/e71828/pi_ina226.git

FROM python:3.8-slim-buster

WORKDIR /opt
COPY --from=builder pi_ina226 /opt/pi_ina226
RUN cd /opt/pi_ina226 && python setup.py install
RUN pip install paho-mqtt

ENV BUSNUM 1
ENV MAXEXAMPS 10
ENV MQTT_SERVICE_HOST mosquitto.local
ENV MQTT_SERVICE_PORT 1883
ENV MQTT_SERVICE_TOPIC home/livingroom
ENV MQTT_CLIENT_ID ina226-mqtt-service

COPY ina226-mqtt.py /opt/ina226-mqtt.py
ENTRYPOINT ["python", "/opt/ina226-mqtt.py"]
