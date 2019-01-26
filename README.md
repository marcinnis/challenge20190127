# SRE CHALLENGE

## 0. Overview

Attached package consists of 3 parts:
- **src** - directory with files needed to execute requested solution
- **Dockerfile** - file needed to build docker image
- **README.md** - this file

## 1. DOCKER

Dockerfile has 3 variables:
- **LOCAL_LISTENER** - at which port application will listen for DNS queries (default 53)
- **DNS_IP** - remote DNS over TLS IP address (default 1.0.0.1)
- **DNS_PORT** - remote DNS over TLS port (default 853)

In order to build image
```
docker build -t dnsovertlsproxy .
```

Execution (in this case exposing port 53 udp and tcp):
```
docker run -p 53:53/tcp -p 53:53/udp -it dnsovertlsproxy
```

Test with TCP:
```
dig +tcp @IPADDRES -p PORT DOMAIN_NAME
```

Test with UDP:
```
dig +notcp @IPADDRES -p PORT DOMAIN_NAME
```

Script usage:
```
usage: app-final.py [-h] -i <server-ip> -p <server-port> [-l <local-port>]

DNS over TLS implementation

optional arguments:
  -h, --help            show this help message and exit
  -i <server-ip>, --dns-ip <server-ip>
                        Remote DNS-over-TLS server IP address
  -p <server-port>, --dns-port <server-port>
                        Remote DNS-over-TLS server port
  -l <local-port>, --local-port <local-port>
                        Local port for DNS queries listener
```

## 2. SOLUTION

### Overview

Application meets minimal requirements - handling DNS queries, forwarding these to defined DNS over TLS server (here by default Cloudflare server is in use) and then returning results to user.
Application is written in Python.
Minimal *python:3.6-alpine* docker image is used as a base.

### Implemented improvements

Application allows multiple incoming requests at the same time. Feature has been implemented using *socketserver*, which can manage multiple threads.

On top of that support for both TCP and UDP traffic has been implemented.

## 3. REMARKS

### Microservice architecture

Regarding Microservice architecture I would not use such tool as direct resolver for all the DNS queries. I would use some DNS caching solution (like *dnsmasq*) and only then behind it - queries would be routed to DNS over TLS proxy.

In case of implementation in *Kubernetes* - it is needed to change default dnsPolicy and set it to *ClusterFirst*. This way queries will be forwarded to upstream nameserver inherited from the node.
And then in CoreDNS (assuming new Kubernetes DNS service is in use) we should change ConfigMap configuration and set IPs of our DNS-over-TLS proxy as default resolver.

### Security concerns / potential improvements

Due to security concerns and best practices application forces using TLSv1.2.
It also verifies if remote DNS server's certificate is trusted via CA store. Additionally it would be worth to add additional checkup - if the hostname configured in SSL certificate matches real hostname of remote DNS server.

Beside that in production implementation I would consider using following improvements:

- any system monitoring and controlling if application is running properly inside docker image should be considered
- more remote DNS over TLS servers to be used. Preferably in load balanced mode
- verification and validation of DNS messages
- better connection management
  - as mentioned above DNS queries caching solution (like dnsmasq) should be consider
  - connection pooling (reusing existing ones) could be implemented
- (much) better error handling
- (much) better logging
- verification of users’ inputs
- unit tests
- currently, for simplification application is executed by user root (inside of docker). This is not recommended in production, so dedicated user with limited access should be used  
- option to enable only TCP or UDP could be implemented (but it can also be controlled via ports exposed through Docker)
- for simplification CA certificate is also part of the attached package - but of course in production environment it should be done different way … for example putting all certificates inside of docker image and keep it in private repository
