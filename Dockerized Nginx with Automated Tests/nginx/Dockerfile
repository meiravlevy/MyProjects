FROM ubuntu:24.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Nginx and OpenSSL, create self-signed certificate, 
# and remove apt cache
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx openssl \
    && mkdir -p /etc/nginx/ssl \
    && openssl req -x509 -nodes -newkey rsa:2048 \
       -keyout /etc/nginx/ssl/server.key \
       -out /etc/nginx/ssl/server.crt \
       -days 365 \
       -subj "/CN=localhost" \
    && rm -rf /var/lib/apt/lists/*

COPY config/nginx.conf /etc/nginx/nginx.conf
COPY src/html /usr/share/nginx/html

EXPOSE 8080 9090 8443

CMD ["nginx", "-g", "daemon off;"]