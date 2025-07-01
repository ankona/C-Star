CI_DIR		:= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
ACCOUNT		:= "ankona"
VERSION		:= "1"
REPO_URI	:= "docker.io"


IMG_BUILDBASE := "buildbase"
.PHONY: buildbase
buildbase:
	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_BUILDBASE)" $(IMG_BUILDBASE) $(ACCOUNT) $(VERSION) $(REPO_URI)

IMG_MPI := "mpi"
.PHONY: mpi
mpi: buildbase
	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_MPI)" $(IMG_MPI) $(ACCOUNT) $(VERSION) $(REPO_URI)

IMG_MPI507 := "mpi-5.0.7"
.PHONY: mpi5
mpi5: buildbase
	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_MPI507)" $(IMG_MPI507) $(ACCOUNT) $(VERSION) $(REPO_URI)

IMG_MPICH422 := "mpich-4.2.2"
.PHONY: mpich
mpich: buildbase
	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_MPICH422)" $(IMG_MPICH422) $(ACCOUNT) $(VERSION) $(REPO_URI)

IMG_HDF5 := "hdf5"
.PHONY: hdf5
hdf5: buildbase mpi5
	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_HDF5)" $(IMG_HDF5) $(ACCOUNT) $(VERSION) $(REPO_URI)

IMG_NETCDF := "netcdf"
.PHONY: netcdf
netcdf: buildbase hdf5
	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_NETCDF)" $(IMG_NETCDF) $(ACCOUNT) $(VERSION) $(REPO_URI)

IMG_IFX := "ifx"
.PHONY: ifx
ifx: buildbase
	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_IFX)" $(IMG_IFX) $(ACCOUNT) $(VERSION) $(REPO_URI)

# IMG_GCC := "gcc"
# .PHONY: gcc
# gcc: buildbase
# 	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_GCC)" $(IMG_GCC) $(ACCOUNT) $(VERSION) $(REPO_URI)

IMG_CONDA := "condabase"
.PHONY: conda
conda:
	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_CONDA)" $(IMG_CONDA) $(ACCOUNT) $(VERSION) $(REPO_URI)

IMG_RUNNER := "runner"
.PHONY: runner
runner: hdf5 netcdf condabase # gcc
	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_RUNNER)" $(IMG_RUNNER) $(ACCOUNT) $(VERSION) $(REPO_URI)

IMG_WORKER := "worker"
.PHONY: worker
worker: runner
	$(CI_DIR)build.sh "$(CI_DIR)$(IMG_WORKER)" $(IMG_WORKER) $(ACCOUNT) $(VERSION) $(REPO_URI)


.PHONY: allmpi
allmpi: mpi mpich mpi5

.PHONY: login
login:
	podman-hpc login "$(REPO_URI)"

.PHONY: all
all: allmpi runner ifx
