FROM ubuntu:20.04
LABEL type="az-usage-exporter"

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3.9-dev python3-pip && apt-get clean
COPY . /opt/az_usage_exporter
RUN pip install --no-cache-dir -r /opt/az_usage_exporter/requirements.txt

WORKDIR /opt/az_usage_exporter

CMD ["python3","main.py"]