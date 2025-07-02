FROM ankona/cstar-buildbase:1


# ARG OPENMPI_URI="https://download.open-mpi.org/release/open-mpi/v5.0/openmpi-5.0.7.tar.gz"
# ARG OMPI_TGZ_NAME="openmpi-5.0.7.tar.gz" 
# ARG OMPI_TGZ_OUT_DIR="openmpi-5.0.7"

ARG HOME="/root"
ARG SRC_DIR="/install"
ARG INSTALL_BASE_DIR="/opt"
ENV MPIHOME="$INSTALL_BASE_DIR/$OMPI_TGZ_OUT_DIR"

ARG OMPI_ENV="$HOME/ompi.env"

# apt-get install flex
# VERSION=4.1.6
# git clone https://github.com/open-mpi/ompi.git --recursive
# cd ompi
# git checkout v$VERSION --
# # git submodule update --init --recursive
# export AUTOMAKE_JOBS=32
# ./autogen.pl
# OPTIONS="--with-pic"  # no --with-slurm -> this actually seems to break ...
# INSTALL_PREFIX=/opt/ompi-$VERSION
# mkdir -p /opt/ompi-$VERSION


# for install from source, see:
# https://webpages.charlotte.edu/abw/coit-grid01.uncc.edu/ParallelProgSoftware/Software/OpenMPIInstall.pdf
#RUN apt-get update && apt-get install -y build-essential
#RUN apt-get install -y openmpi-bin openmpi-doc libopenmpi-dev

# RUN mkdir -p $SRC_DIR

# WORKDIR $SRC_DIR
# RUN wget $OPENMPI_URI && \
#     tar xvf $OMPI_TGZ_NAME && \
#     cd $OMPI_TGZ_OUT_DIR && \
#     ./configure \
#         --prefix=$MPIHOME --with-pic \
#         --with-slurm \
#         --with-pmix=internal && \
#     make -j $(nproc) && make install && cd $SRC_DIR && \
#     rm $OMPI_TGZ_NAME && \
#     rm -rf $OMPI_TGZ_OUT_DIR

# ENV PATH=$MPIHOME/bin:$PATH
# ENV LD_LIBRARY_PATH=$MPIHOME/lib:$LD_LIBRARY_PATH
# ENV CPATH=$MPIHOME/include:$CPATH
# ENV LIBRARY_PATH=$MPIHOME/lib:$LIBRARY_PATH
# ENV LD_RUN_PATH=$MPIHOME/lib:$LD_RUN_PATH

# RUN mkdir -p "${HOME}" && touch $OMPI_ENV && \
#     echo "export MPIHOME=$MPIHOME" >> $OMPI_ENV && \
#     echo 'export PATH=$MPIHOME/bin:$PATH' >> $OMPI_ENV && \
#     echo 'export LD_LIBRARY_PATH=$MPIHOME/lib:$LD_LIBRARY_PATH' >> $OMPI_ENV && \
#     echo 'export CPATH=$MPIHOME/include:$CPATH' >> $OMPI_ENV && \
#     echo 'export LIBRARY_PATH=$MPIHOME/lib:$LIBRARY_PATH' >> $OMPI_ENV && \
#     echo 'export LD_RUN_PATH=$MPIHOME/lib:$LD_RUN_PATH' >> $OMPI_ENV && \
#     cat $OMPI_ENV >> $HOME/.profile && cat $OMPI_ENV >> $HOME/.bashrc

WORKDIR /opt
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y build-essential ca-certificates automake autoconf \
    python3-dev python3-pip python3-mpi4py wget libpmi2-0-dev --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

ENV openmpi_version=4.1.4

RUN openmpi_version=$openmpi_version && \
    wget https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-$openmpi_version.tar.gz && \
    tar xf openmpi-$openmpi_version.tar.gz && \
    cd openmpi-$openmpi_version && \
    ./configure --prefix=/opt/openmpi --with-slurm \
        --with-pmi=/usr/include/slurm \
        --with-pmi-libdir=/usr/lib/x86_64-linux-gnu \
        CFLAGS=-I/usr/include/slurm && \
    make -j$nproc && \
    make install && \
    cd .. && \
    rm -rf openmpi-$openmpi_version.tar.gz openmpi-$openmpi_version

RUN openmpi_version=$openmpi_version && \
    /sbin/ldconfig

ENV PATH=/opt/openmpi/bin:$PATH
# RUN python3 -m pip install mpi4py

ENV OMPI_ALLOW_RUN_AS_ROOT=1
ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

ARG RING_URI="https://gist.githubusercontent.com/ankona/42bd3fd28cbeec4da65ed57f0529b8dc/raw/3e0a3b7cac0536a0726a5fb36aceb5db1dba8506/ring.c"
ADD $RING_URI $INSTALL_BASE_DIR/ring.c
RUN mpicc $INSTALL_BASE_DIR/ring.c -o $INSTALL_BASE_DIR/ring && chmod 777 $INSTALL_BASE_DIR/ring

# # ARG $PMIX_V="6.0.0"
# # ENV PMIX_ROOT=$INSTALL_BASE_DIR/pmix-6.0.0

# # # RUN apt-get update && apt-get install python3 python3-devel Cython

# # WORKDIR $SRC_DIR
# # RUN wget "https://github.com/openpmix/openpmix/releases/download/v6.0.0/pmix-6.0.0.tar.gz" && \
# #     tar xf "pmix-6.0.0.tar.gz" && \
# #     cd pmix-6.0.0 && \
# #     ./configure --prefix=/opt/pmix-6.0.0 && \
# #     make -j $(nproc) all && \
# #     make install

# # ENV LD_LIBRARY_PATH=$PMIX_ROOT/lib:$LD_LIBRARY_PATH
# # ENV PATH=$PMIX_ROOT/bin:$PATH


# # RUN echo "export PMIX_ROOT=$PMIX_ROOT" >> $OMPI_ENV && \
# #     echo 'export LD_LIBRARY_PATH=$PMIX_ROOT/lib:$LD_LIBRARY_PATH' >> $OMPI_ENV && \
# #     echo 'export PATH=$PMIX_ROOT/bin:$PATH' >> $OMPI_ENV && \
# #     cat $OMPI_ENV >> $HOME/.profile && cat $OMPI_ENV >> $HOME/.bashrc

# # CMD ["mpirun", "--allow-run-as-root", "./foo"]
# # ENTRYPOINT ["mpirun", "--allow-run-as-root"]
