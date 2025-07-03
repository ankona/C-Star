FROM ankona/cstar-roms-pb:1 AS roms_prebuilt

ARG REPO_MARBL="https://github.com/marbl-ecosys/MARBL/archive/refs/tags/marbl0.45.0.tar.gz"

ENV INSTALL_BASE_DIR=/opt
ENV MARBL_ROOT=$INSTALL_BASE_DIR/MARBL
ENV OMPI_ALLOW_RUN_AS_ROOT=1
ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

# Install MARBL
# (Makefile doesn't define ifx option but setting I_MPI_F90 to ifx above should fix this)
WORKDIR $INSTALL_BASE_DIR
RUN source /opt/intel/oneapi/setvars.sh && \
    wget -q $REPO_MARBL && \
    tar xvf marbl0.45.0.tar.gz && \
    mv MARBL-marbl0.45.0 $MARBL_ROOT && \
    cd $MARBL_ROOT/src && \
    make intel USEMPI=TRUE

ENTRYPOINT [ "mpiexec", "--allow-run-as-root", "hostname"]
