FROM ankona/cstar-buildbase:1

ARG MPICH_URI="https://www.mpich.org/static/downloads/4.2.2/mpich-4.2.2.tar.gz"
ARG MPI_TGZ_NAME="mpich-4.2.2.tar.gz" 
ARG MPI_TGZ_OUT_DIR="mpich-4.2.2"

ARG HOME="/root"
ARG SRC_DIR="/install"
ARG INSTALL_BASE_DIR="/opt"
ENV MPIHOME="$INSTALL_BASE_DIR/$MPI_TGZ_OUT_DIR"

ARG OMPI_ENV="$HOME/ompi.env"


# for install from source, see:
# https://webpages.charlotte.edu/abw/coit-grid01.uncc.edu/ParallelProgSoftware/Software/OpenMPIInstall.pdf
RUN apt-get update && apt-get install -y build-essential
RUN mkdir -p $SRC_DIR

# TODO: get rid of OMPI in the base image? ompi_info still works here and it should not?

WORKDIR $SRC_DIR
RUN wget $MPICH_URI && \
    tar xvf $MPI_TGZ_NAME && \
    cd $MPI_TGZ_OUT_DIR && \
    ./configure \
        --prefix=$MPIHOME CC=gcc CXX=g++ FC=gfortran \
        --with-pmi=pmi2 && \
    #  --enable-shared 
    #  --with-pic \
        # --with-slurm \
        # --with-pmix=internal && \
    make -j $(nproc) && make install && cd $SRC_DIR && \
    rm $MPI_TGZ_NAME && \
    rm -rf $MPI_TGZ_OUT_DIR


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

WORKDIR $SRC_DIR
ARG RING_URI="https://gist.githubusercontent.com/ankona/42bd3fd28cbeec4da65ed57f0529b8dc/raw/3e0a3b7cac0536a0726a5fb36aceb5db1dba8506/ring.c"
ADD $RING_URI $INSTALL_BASE_DIR/ring.c
RUN mpicc $INSTALL_BASE_DIR/ring.c -o $INSTALL_BASE_DIR/ring && chmod 777 $INSTALL_BASE_DIR/ring

# ARG $PMIX_V="6.0.0"
# ENV PMIX_ROOT=$INSTALL_BASE_DIR/pmix-6.0.0

# # RUN apt-get update && apt-get install python3 python3-devel Cython

# WORKDIR $SRC_DIR
# RUN wget "https://github.com/openpmix/openpmix/releases/download/v6.0.0/pmix-6.0.0.tar.gz" && \
#     tar xf "pmix-6.0.0.tar.gz" && \
#     cd pmix-6.0.0 && \
#     ./configure --prefix=/opt/pmix-6.0.0 && \
#     make -j $(nproc) all && \
#     make install

# ENV LD_LIBRARY_PATH=$PMIX_ROOT/lib:$LD_LIBRARY_PATH
# ENV PATH=$PMIX_ROOT/bin:$PATH

# RUN echo "export PMIX_ROOT=$PMIX_ROOT" >> $OMPI_ENV && \
#     echo 'export LD_LIBRARY_PATH=$PMIX_ROOT/lib:$LD_LIBRARY_PATH' >> $OMPI_ENV && \
#     echo 'export PATH=$PMIX_ROOT/bin:$PATH' >> $OMPI_ENV && \
#     cat $OMPI_ENV >> $HOME/.profile && cat $OMPI_ENV >> $HOME/.bashrc

# CMD ["mpirun", "--allow-run-as-root", "./foo"]
# ENTRYPOINT ["mpirun", "--allow-run-as-root"]
