ARG SRC_DIR="/install"
ARG INSTALL_BASE_DIR="/opt"

ARG HDF5_INSTALL_DIR="hdf5-1.14.6-install"
ARG HDF5_SRC=$SRC_DIR/hdf5-hdf5_1.14.6
ARG HDF5_HOME=$INSTALL_BASE_DIR/$HDF5_INSTALL_DIR

ARG NETCDF_V="4.9.3"
ARG NETCDF_TAR="v$NETCDF_V.tar.gz"
ARG NETCDF_URL="https://github.com/Unidata/netcdf-c/archive/refs/tags/$NETCDF_TAR"

ARG NETCDF_FV="4.6.2"
ARG NETCDF_FORTRAN_TAR="v$NETCDF_FV.tar.gz"
ARG NETCDF_FORTRAN_URL="https://github.com/Unidata/netcdf-fortran/archive/refs/tags/$NETCDF_FORTRAN_TAR"
ARG NETCDF_FORTRAN_DIR="netcdf-fortran-$NETCDF_FV-install"

ARG HOME="/root"

ARG NETCDF_SRC=$SRC_DIR/netcdf-c-$NETCDF_V
ARG NETCDF_HOME=$INSTALL_BASE_DIR/netcdf-$NETCDF_V-install

ARG NETCDF_FORTRAN_SRC=$SRC_DIR/netcdf-fortran-$NETCDF_FV
ARG NETCDF_FORTRAN_HOME=$INSTALL_BASE_DIR/$NETCDF_FORTRAN_DIR


ARG HDF5_ENV="${HOME}/hdf5.env"
ARG NCDF_ENV="${HOME}/netcdf.env"

# Must first prep & install netcdf to build hdf
FROM ankona/cstar-hdf5:1 as stage_hdf
ARG HDF5_SRC
ARG HDF5_HOME
ARG HDF5_INSTALL_DIR
ARG HOME
ARG HDF5_ENV

# perform installation
WORKDIR $HDF5_SRC
RUN . $HDF5_ENV && make -j $(nproc) && make install


FROM ankona/cstar-mpi-5.0.7:1 as stage_netcdf
ARG SRC_DIR
ARG NETCDF_URL
ARG NETCDF_TAR
ARG HDF5_HOME
ARG HOME
ARG NETCDF_HOME
ARG NETCDF_FORTRAN_HOME
ARG NETCDF_FORTRAN_URL
ARG NETCDF_FORTRAN_TAR
ARG NETCDF_SRC
ARG NETCDF_FORTRAN_SRC
ARG HDF5_ENV
ARG NCDF_ENV

COPY --from=stage_hdf $HDF5_ENV $HDF5_ENV
COPY --from=stage_hdf $HDF5_HOME $HDF5_HOME

WORKDIR $SRC_DIR
RUN wget -q $NETCDF_URL && \
    tar xvf ./$NETCDF_TAR && \
    rm ./$NETCDF_TAR

WORKDIR $NETCDF_SRC
# RUN gcc --version && g++ --version && gfortran --version && \
#     mpicc --version && mpicxx --version
# ENV NETCDF_HOME=$NETCDF_HOME

RUN . $HDF5_ENV && \
    mkdir -p $NETCDF_HOME && \
    ./configure --prefix=$NETCDF_HOME \
    CC=gcc FC=gfortran \
    CFLAGS="-O3 -march=x86-64 -I$HDF5_HOME/include" \
    LDFLAGS="-L$HDF5_HOME/lib" \
    --enable-netcdf-4 --enable-shared
    # removed -align from CFLAGS

# RUN . $HDF5_ENV && make -j $(nproc)
# # RUN make install
# # RUN rm -rf $NETCDF_SRC
# ENV NETCDFHOME=$NETCDF_HOME/lib
ENV NETCDF_FORTRAN_HOME=$NETCDF_FORTRAN_HOME

RUN echo "export NETCDF_HOME=$NETCDF_HOME" >> $NCDF_ENV && \
    echo "export NETCDF_FORTRAN_HOME=$NETCDF_FORTRAN_HOME" >> $NCDF_ENV && \
    echo 'export PATH=$NETCDF_FORTRAN_HOME/bin:$NETCDF_HOME/bin:$PATH' >> $NCDF_ENV && \
    echo 'export LD_LIBRARY_PATH=$NETCDF_FORTRAN_HOME/lib:$NETCDF_HOME/lib:$LD_LIBRARY_PATH' >> $NCDF_ENV && \
    echo 'export CPATH=$NETCDF_FORTRAN_HOME/include:$NETCDF_HOME/include:$CPATH' >> $NCDF_ENV && \
    echo 'export LIBRARY_PATH=$NETCDF_FORTRAN_HOME/lib:$NETCDF_HOME/lib:$LIBRARY_PATH' >> $NCDF_ENV
    # echo "export NETCDFHOME=$NETCDF_HOME/lib" >> $NCDF_ENV && \

# Install and configure NetCDF-Fortran
WORKDIR $SRC_DIR
RUN wget -q $NETCDF_FORTRAN_URL && \
    tar xvf ./$NETCDF_FORTRAN_TAR && \
    rm ./$NETCDF_FORTRAN_TAR

WORKDIR $NETCDF_FORTRAN_SRC
RUN . $HDF5_ENV && \
    . $NCDF_ENV && \
    mkdir -p $NETCDF_FORTRAN_HOME && \
    ./configure --prefix=$NETCDF_FORTRAN_HOME \
    CC=mpicc FC=gfortran \
    CFLAGS="-O3 -march=x86-64 -I$NETCDF_HOME/include" \
    FFLAGS="-O3 -march=x86-64 -I$NETCDF_HOME/include" \
    LDFLAGS="-L$NETCDF_HOME/lib" \
    --enable-shared
    # removed -align from cflags and fflags

# RUN make -j $(nproc) && \
#     make install && \
#     rm -rf $NETCDF_FORTRAN_SRC

# RUN . $HDF5_ENV && \
#     . $NCDF_ENV && \
#     make -j $(nproc)
    # make install && \
    # rm -rf $NETCDF_FORTRAN_SRC


FROM ankona/cstar-buildbase:1 as stage_out
ARG HOME
ARG NETCDF_SRC
ARG NETCDF_FORTRAN_SRC
ARG HDF5_ENV
ARG NCDF_ENV

COPY --from=stage_hdf $HDF5_ENV $HDF5_ENV
COPY --from=stage_netcdf $NCDF_ENV $NCDF_ENV
COPY --from=stage_netcdf $NETCDF_SRC $NETCDF_SRC
COPY --from=stage_netcdf $NETCDF_FORTRAN_SRC $NETCDF_FORTRAN_SRC
