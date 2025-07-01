# FROM ankona/cstar-gcc-pb:1 AS compiler
FROM ankona/cstar-base:1 as dependencies

ARG SRC_DIR="/install"
ARG INSTALL_BASE_DIR=/opt
ARG ROMS_ROOT=$INSTALL_BASE_DIR/ucla-roms 
ARG ROMS_PATH=$ROMS_ROOT/Tools-Roms/
ARG REPO_ROMS="https://github.com/dafyddstephenson/ucla-roms/archive/refs/heads/update_makefiles.tar.gz"
ENV HOME="/root"
ENV BASE_ENV="${HOME}/base.env"
ENV ROOT_ENV="${HOME}/.profile"
ENV BASH_ENV="${HOME}/.bash_profile"

# RUN apt-get update && apt-get install -y build-essential
# RUN apt-get install -y openmpi-bin openmpi-doc libopenmpi-dev
# RUN mv /opt/intel/oneapi/mpi/2021.14/bin/mpiexec /opt/intel/oneapi/mpi/2021.14/bin/mpiexec.bak
# RUN mv /opt/intel/oneapi/mpi/2021.14/bin/mpicc /opt/intel/oneapi/mpi/2021.14/bin/mpicc.bak

# ENV PATH=$PATH:$ROMS_PATH
# ENV OMPI_ALLOW_RUN_AS_ROOT=1
# ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
# ENV ROMS_ROOT=$ROMS_ROOT

WORKDIR $SRC_DIR

RUN cat $BASE_ENV >> $ROOT_ENV && \
    cat $ROOT_ENV >> $BASH_ENV && \
    echo "export ROMS_ROOT=$ROMS_ROOT" >> $ROOT_ENV && \
    echo "export ROMS_PATH=$ROMS_PATH" >> $ROOT_ENV && \
    echo 'export PATH=$PATH:$ROMS_PATH' >> $ROOT_ENV && \
    echo 'export OMPI_ALLOW_RUN_AS_ROOT=1' >> $ROOT_ENV && \
    echo 'export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1' >> $ROOT_ENV

RUN . $ROOT_ENV && \
    wget $REPO_ROMS && \
    tar xvf update_makefiles.tar.gz && \
    mv ucla-roms-update_makefiles $ROMS_ROOT && \
    rm update_makefiles.tar.gz

RUN . $ROOT_ENV && \
    cd $ROMS_ROOT/Work && \
    make nhmg COMPILER=gnu

# RUN . $ROOT_ENV && \
#     cd $ROMS_PATH && \
#     make COMPILER=gnu
