ARG IMG_IFX="ankona/cstar-ifx:latest"

FROM $IMG_IFX AS compiler


ARG INSTALL_BASE_DIR=/opt
ARG ROMS_ROOT=$INSTALL_BASE_DIR/ucla-roms 
ARG ROMS_PATH=$ROMS_ROOT/Tools-Roms/
ARG REPO_ROMS="https://github.com/dafyddstephenson/ucla-roms/archive/refs/heads/update_makefiles.tar.gz"

# RUN apt-get update && apt-get install -y --no-install-recommends build-essential
# RUN apt-get install -y openmpi-bin openmpi-doc libopenmpi-dev
# RUN mv /opt/intel/oneapi/mpi/2021.14/bin/mpiexec /opt/intel/oneapi/mpi/2021.14/bin/mpiexec.bak
# RUN mv /opt/intel/oneapi/mpi/2021.14/bin/mpicc /opt/intel/oneapi/mpi/2021.14/bin/mpicc.bak

ENV PATH=$PATH:$ROMS_PATH
ENV COMPILER="intel"
WORKDIR $INSTALL_BASE_DIR

# Install and configure ROMS
RUN source /opt/intel/oneapi/setvars.sh && \
    wget -q "$REPO_ROMS" && \
    tar xvf update_makefiles.tar.gz && \
    mv ucla-roms-update_makefiles "$ROMS_ROOT" && \
    cd "$ROMS_ROOT/Work" && \
    make nhmg COMPILER=$COMPILER && \
    cd "$ROMS_PATH" && \
    make COMPILER=$COMPILER