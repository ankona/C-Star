# ARG MAIN_STAGE="main"  # pass `add_test` to build the test program /runtest


FROM ubuntu:24.04 as main

ENV TERM="xterm-256color"

RUN apt-get update && \
    apt-get install -y \
        binutils \
        build-essential \
        ca-certificates \
        git \
        gfortran \
        libstdc++-14-dev \
        libxml2-dev \
        libcurl4-openssl-dev \
        m4 \
        python3 \
        python-is-python3 \
        rsync \
        wget \
        zlib1g-dev \
        # openmpi-bin \
        # openmpi-doc \
        # libopenmpi-dev \
        # libpmi2-0-dev \
        # libnetcdf-dev \
        # libhdf5-serial-dev \
        --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    ldconfig


# FROM main as add_test

# ARG TEST_ENV="/etc/profile.d/99-ring.sh"
# ENV RING_URI="https://gist.githubusercontent.com/ankona/42bd3fd28cbeec4da65ed57f0529b8dc/raw/3e0a3b7cac0536a0726a5fb36aceb5db1dba8506/ring.c"

# ENV MPI_TEST_HARNESS="/test/ring"
# ENV PATH="/test:$PATH"
# RUN mkdir -p "/test" && \
#     mkdir -p "/etc/profile.d" && \
#     wget -q "$RING_URI" -O "/test/ring.c" && \
#     # mpicc "/test/ring.c" -o $MPI_TEST_HARNESS && \
#     rm "/test/ring.c" && \
#     echo "#!/bin/bash" >> "$TEST_ENV" && \
#     echo "export MPI_TEST_HARNESS=$MPI_TEST_HARNESS" >> "$TEST_ENV" && \
#     printf '#!/bin/bash\nmpirun -n 2 --allow-run-as-root %s\n' "$MPI_TEST_HARNESS" >> "/test/runtest" && \
#     chmod +x "$TEST_ENV" && \
#     chmod +x "/test/runtest" && \
#     apt-get update && \
#     apt-get install -y neovim && \
#     rm -rf /var/lib/apt/lists/*


# FROM $MAIN_STAGE as final

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD []
ENTRYPOINT ["/entrypoint.sh"]
