FROM ankona/cstar-buildbase:1

ARG OPENMPI_URI="https://download.open-mpi.org/release/open-mpi/v5.0/openmpi-5.0.7.tar.gz"
ARG OMPI_TGZ_NAME="openmpi-5.0.7.tar.gz" 
ARG OMPI_TGZ_OUT_DIR="openmpi-5.0.7"

ARG HOME="/root"
ARG SRC_DIR="/install"
ARG INSTALL_BASE_DIR="/opt"
ENV MPIHOME="$INSTALL_BASE_DIR/$OMPI_TGZ_OUT_DIR"
ARG OMPI_ENV="$HOME/ompi.env"

RUN mkdir -p $SRC_DIR

WORKDIR $SRC_DIR
RUN wget $OPENMPI_URI && \
    tar xvf $OMPI_TGZ_NAME && \
    cd $OMPI_TGZ_OUT_DIR && \
    ./configure \
        --prefix=$MPIHOME --with-pic \
        --with-slurm \
        --with-pmix=internal && \
    make -j $(nproc) && make install && cd $SRC_DIR && \
    rm $OMPI_TGZ_NAME && \
    rm -rf $OMPI_TGZ_OUT_DIR

ENV PATH=$MPIHOME/bin:$PATH
ENV LD_LIBRARY_PATH=$MPIHOME/lib:$LD_LIBRARY_PATH
ENV CPATH=$MPIHOME/include:$CPATH
ENV LIBRARY_PATH=$MPIHOME/lib:$LIBRARY_PATH
ENV LD_RUN_PATH=$MPIHOME/lib:$LD_RUN_PATH

RUN mkdir -p "${HOME}" && touch $OMPI_ENV && \
    echo "export MPIHOME=$MPIHOME" >> $OMPI_ENV && \
    echo 'export PATH=$MPIHOME/bin:$PATH' >> $OMPI_ENV && \
    echo 'export LD_LIBRARY_PATH=$MPIHOME/lib:$LD_LIBRARY_PATH' >> $OMPI_ENV && \
    echo 'export CPATH=$MPIHOME/include:$CPATH' >> $OMPI_ENV && \
    echo 'export LIBRARY_PATH=$MPIHOME/lib:$LIBRARY_PATH' >> $OMPI_ENV && \
    echo 'export LD_RUN_PATH=$MPIHOME/lib:$LD_RUN_PATH' >> $OMPI_ENV && \
    cat $OMPI_ENV >> $HOME/.profile && cat $OMPI_ENV >> $HOME/.bashrc

RUN /sbin/ldconfig

ENV OMPI_ALLOW_RUN_AS_ROOT=1
ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

ARG RING_URI="https://gist.githubusercontent.com/ankona/42bd3fd28cbeec4da65ed57f0529b8dc/raw/3e0a3b7cac0536a0726a5fb36aceb5db1dba8506/ring.c"
ADD $RING_URI $INSTALL_BASE_DIR/ring.c
RUN mpicc $INSTALL_BASE_DIR/ring.c -o $INSTALL_BASE_DIR/ring && chmod 777 $INSTALL_BASE_DIR/ring
