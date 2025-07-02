ARG SRC_DIR="/install"
ARG INSTALL_BASE_DIR="/opt"
ARG HOME="/root"
ARG HDF5_ENV="${HOME}/hdf5.env"

FROM ankona/cstar-mpi-5.0.7:1

ARG HOME
ARG HDF5_ENV
ARG SRC_DIR
ARG INSTALL_BASE_DIR
ARG HDF5_INSTALL_DIR="hdf5-1.14.6-install"
ARG HDF5_TAR="hdf5_1.14.6.tar.gz"
ARG HDF5_URL="https://github.com/HDFGroup/hdf5/archive/refs/tags/hdf5_1.14.6.tar.gz"

ENV HDF5_HOME=$INSTALL_BASE_DIR/$HDF5_INSTALL_DIR
ENV HDF5_SRC=$SRC_DIR/hdf5-hdf5_1.14.6

WORKDIR $SRC_DIR
RUN wget -q $HDF5_URL && \
    tar xvf ./$HDF5_TAR && \
    rm ./$HDF5_TAR

WORKDIR $HDF5_SRC
RUN mkdir -p $HDF5_HOME && \
    ./configure --prefix=$HDF5_HOME \
    CC=mpicc FC=gfortran CXX=mpicxx \
    CFLAGS="-fPIC -O3 -march=x86-64" \
    FFLAGS="-fPIC -O3 -march=x86-64" \
    CXXFLAGS="-fPIC -O3 -march=x86-64" \
    --enable-fortran --enable-shared --with-pic

# confirm these replacements...
# using mpicc, gfortran, mpicxx
# CC=mpiicx FC=mpiifx CXX=mpiicpc
ENV PATH="$HDF5_HOME/bin:$PATH"
ENV LD_LIBRARY_PATH="$HDF5_HOME/lib:$LD_LIBRARY_PATH"
ENV CPATH="$HDF5_HOME/include:$CPATH"
ENV LIBRARY_PATH="$HDF5_HOME/lib:$LIBRARY_PATH"
ENV LD_RUN_PATH="$HDF5_HOME/lib:$LD_RUN_PATH"

RUN make -j $(nproc) && make install

RUN mkdir -p "${HOME}" && touch $HDF5_ENV && \
    # echo 'export HDF5_SRC=$HDF5_SRC" >> $HDF5_ENV && \
    echo "export HDF5_HOME=$HDF5_HOME" >> $HDF5_ENV && \
    echo 'export PATH=$HDF5_HOME/bin:$PATH' >> $HDF5_ENV && \
    echo 'export LD_LIBRARY_PATH=$HDF5_HOME/lib:$LD_LIBRARY_PATH' >> $HDF5_ENV && \
    echo 'export CPATH=$HDF5_HOME/include:$CPATH' >> $HDF5_ENV && \
    echo 'export LIBRARY_PATH=$HDF5_HOME/lib:$LIBRARY_PATH' >> $HDF5_ENV && \
    echo 'export LD_RUN_PATH=$HDF5_HOME/lib:$LD_RUN_PATH' >> $HDF5_ENV
