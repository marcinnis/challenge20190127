FROM python:3.6-alpine
ARG LOCAL_LISTENER=53
ENV LOCAL_LISTENER=${LOCAL_LISTENER}
ARG DNS_IP=1.0.0.1
ARG DNS_PORT=853
ENV DNS_IP=${DNS_IP}
ENV DNS_PORT=${DNS_PORT}
WORKDIR /
COPY src/app-final.py /
COPY src/ca-certificates.crt /
CMD python app-final.py --dns-ip $DNS_IP --dns-port $DNS_PORT --local-port $LOCAL_LISTENER
