FROM ubuntu:24.04

RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*

ARG INSTALL_BASE_DIR="/opt"
ENV TERM=xterm-256color

WORKDIR $INSTALL_BASE_DIR

RUN apt-get update && \
    apt-get install -y \
        build-essential automake autoconf \
        gcc g++ gfortran binutils \
        libc6-dev libstdc++-14-dev m4 libxml2-dev \
        libcurl4-openssl-dev zlib1g-dev wget \
        python3 python-is-python3 \
        # openmpi-bin openmpi-doc libopenmpi-dev libpmi2-0-dev \
        libnetcdf-dev libhdf5-serial-dev \
        ca-certificates \
        git rsync wget neovim --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

ENV OMPI_ALLOW_RUN_AS_ROOT=1
ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

ARG RING_URI="https://gist.githubusercontent.com/ankona/42bd3fd28cbeec4da65ed57f0529b8dc/raw/3e0a3b7cac0536a0726a5fb36aceb5db1dba8506/ring.c"
ADD $RING_URI $INSTALL_BASE_DIR/ring.c
RUN mpicc $INSTALL_BASE_DIR/ring.c -o $INSTALL_BASE_DIR/ring && chmod 777 $INSTALL_BASE_DIR/ring

# CMD [ "bash" ]
