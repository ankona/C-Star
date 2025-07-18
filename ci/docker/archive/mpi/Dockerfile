ARG IMG_BUILDBASE="ankona/cstar-buildbase:latest"
ARG MAIN_STAGE="main"

FROM $IMG_BUILDBASE as main

SHELL ["/bin/bash", "-c"]

ENV openmpi_minor_version="4.1"
ENV openmpi_version=4.1.4
ARG OMPI_TGZ_NAME="openmpi-$openmpi_version.tar.gz" 
ARG OPENMPI_URI="https://download.open-mpi.org/release/open-mpi/v$openmpi_minor_version/$OMPI_TGZ_NAME"
ARG SRC_DIR="/install"
ARG INSTALL_BASE_DIR="/opt"
ENV OMPI_VERSION_NAME="openmpi-$openmpi_version"
ENV MPIHOME="/opt/$OMPI_VERSION_NAME"
ARG MPI_PROFILE="/etc/profile.d/50-$OMPI_VERSION_NAME.sh"
ENV DEBIAN_FRONTEND noninteractive

# RUN openmpi_version=$openmpi_version && \
WORKDIR "$SRC_DIR"
RUN apt-get update && \
    apt-get install -y \
        libpmi2-0-dev \
        --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    wget -q "$OPENMPI_URI" && \
    tar xf "$OMPI_TGZ_NAME" && \
    cd "$OMPI_VERSION_NAME" && \
    ./configure \
        --prefix="$MPIHOME" \
        --with-slurm \
        --with-pmi=/usr/include/slurm \
        --with-pmi-libdir=/usr/lib/x86_64-linux-gnu \
        CFLAGS=-I/usr/include/slurm && \
    make -j$nproc && \
    make install && \
    rm -rf "$SRC_DIR" && \
    ldconfig

# RUN openmpi_version=$openmpi_version && \
# RUN /sbin/ldconfig

ENV PATH="$MPIHOME/bin:$PATH"
ENV LD_LIBRARY_PATH="$MPIHOME/lib:$LD_LIBRARY_PATH"
ENV CPATH="$MPIHOME/include:$CPATH"
ENV LIBRARY_PATH="$MPIHOME/lib:$LIBRARY_PATH"
ENV LD_RUN_PATH="$MPIHOME/lib:$LD_RUN_PATH"

RUN echo "export MPIHOME=$MPIHOME" >> $MPI_PROFILE && \
    echo 'export PATH=$MPIHOME/bin:$PATH' >> $MPI_PROFILE && \
    echo 'export LD_LIBRARY_PATH=$MPIHOME/lib:$LD_LIBRARY_PATH' >> $MPI_PROFILE && \
    echo 'export CPATH=$MPIHOME/include:$CPATH' >> $MPI_PROFILE && \
    echo 'export LIBRARY_PATH=$MPIHOME/lib:$LIBRARY_PATH' >> $MPI_PROFILE && \
    echo 'export LD_RUN_PATH=$MPIHOME/lib:$LD_RUN_PATH' >> $MPI_PROFILE && \
    echo 'export OMPI_ALLOW_RUN_AS_ROOT=1' >> $MPI_PROFILE && \
    echo 'export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1' >> $MPI_PROFILE


# FROM main as add_test

# ARG TEST_ENV="/etc/profile.d/99-ring.sh"
# ENV RING_URI="https://gist.githubusercontent.com/ankona/42bd3fd28cbeec4da65ed57f0529b8dc/raw/3e0a3b7cac0536a0726a5fb36aceb5db1dba8506/ring.c"

# ENV MPI_TEST_HARNESS="/test/ring"
# ENV PATH="/test:$PATH"
# RUN mkdir -p "/test" && \
#     mkdir -p "/etc/profile.d" && \
#     wget -q "$RING_URI" -O "/test/ring.c" && \
#     mpicc "/test/ring.c" -o $MPI_TEST_HARNESS && \
#     rm "/test/ring.c" && \
#     echo "#!/bin/bash" >> "$TEST_ENV" && \
#     echo "export MPI_TEST_HARNESS=$MPI_TEST_HARNESS" >> "$TEST_ENV" && \
#     printf '#!/bin/bash\nmpirun -n 2 --allow-run-as-root %s\n' "$MPI_TEST_HARNESS" >> "/test/runtest" && \
#     chmod +x "$TEST_ENV" && \
#     chmod +x "/test/runtest" && \
#     apt-get update && \
#     apt-get install -y --no-install-recommends neovim && \
#     rm -rf /var/lib/apt/lists/*


FROM $MAIN_STAGE as final

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD []
ENTRYPOINT ["/entrypoint.sh"]
