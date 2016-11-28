FROM debian:jessie
RUN apt-get update && apt-get install -y socat && apt-get clean
EXPOSE 143
CMD socat -t 100000000 TCP4-LISTEN:143,reuseaddr,fork OPENSSL:$IMAPS_SERVER:imaps,verify=0
