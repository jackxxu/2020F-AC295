# Use the official Debian-hosted Python image
FROM python:3.8-slim-buster

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYENV_SHELL=/bin/bash

# Ensure we have an up to date baseline, install dependencies and create a user
# so we don't run the app as root.
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg graphviz cmake git wget unzip yasm pkg-config libswscale-dev libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libavformat-dev libpq-dev libgtk2.0-dev libatk-adaptor libcanberra-gtk-module x11-apps libgtk-3-dev imagemagick libv4l-dev libdc1394-22-dev qt4-default pandoc && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    useradd -ms /bin/bash app -d /home/app -G sudo -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    chown app:app /app && \
    echo "%sudo ALL=(ALL) NOPASSWD: /usr/local/bin/pip" >> /etc/sudoers

EXPOSE 8081

# Switch to app user
USER app
# Work dir
WORKDIR /app

# Install python packages
ADD Pipfile Pipfile.lock /app/
RUN pipenv sync

# Add source code
ADD . /app

## Entry point
RUN export SHELL=/bin/bash
CMD ["pipenv","shell"]
