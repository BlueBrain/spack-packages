#!/bin/bash
#SBATCH --job-name="build-neuron-stack"
#SBATCH --time=2:00:00
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --account=proj16
#SBATCH --exclusive

#Module issue
export LD_LIBRARY_PATH=/gpfs/bbp.cscs.ch/apps/viz/intel2017/compilers_and_libraries_2017.0.098/linux/mpi/intel64/lib/:$LD_LIBRARY_PATH

##### UNINSTALL PACKAGE #####
uninstall_package() {
    spack uninstall -y -f -d -a neuron
    spack uninstall -y -f -d -a coreneuron
    spack uninstall -y -f -d -a mod2c
    spack uninstall -y -f -d -a nrnh5
    spack uninstall -y -f -d -a reportinglib
    spack uninstall -y -f -d -a neurodamus
    spack uninstall -y -f -d -a neuron-nmodl
}

#### WE WILL INSTALL PYTHON AND HDF5 ONCE
dependency_install() {
    spack install --dirty hdf5 +mpi %gcc ^mvapich2
    spack install --dirty hdf5 +mpi %intel ^intelmpi
}

#### COMPILER TOOLCHAINS ####
compiler_with_mpi=(
    '%intel ^intelmpi'
    '%gcc ^mvapich2'
)

#in case there are inconsistencies
spack reindex

uninstall_package
#spack uninstall -a -f -d -y hdf5

#stop on error
set -e

dependency_install

# hdf5 issue
spack load hdf5 +mpi %gcc ^mvapich2
spack load hdf5 +mpi %intel ^intelmpi

#packages without MPI dependency
spack install --dirty mod2c@develop %intel
spack install --dirty mod2c@github %intel

spack install --dirty mod2c@develop %gcc
spack install --dirty mod2c@github %gcc


for compiler_mpi in "${compiler_with_mpi[@]}"
do
    spack install -v --dirty nrnh5@develop $compiler_mpi

    spack install -v --dirty neuron@develop +mpi $compiler_mpi
    spack install -v --dirty neuron@hdf +mpi $compiler_mpi

    spack install -v --dirty reportinglib $compiler_mpi

    spack install -v --dirty neurodamus@master +compile $compiler_mpi
    spack install -v --dirty neurodamus@develop +compile $compiler_mpi
    spack install -v --dirty neurodamus@hdf +compile $compiler_mpi

    spack install -v --dirty coreneuron@develop +report $compiler_mpi
    spack install -v --dirty coreneuron@github +report $compiler_mpi
    spack install -v --dirty coreneuron@hdf +report $compiler_mpi
done

spack install -v --dirty mod2c@develop %pgi
spack install -v --dirty coreneuron@develop +report %pgi ^mvapich2

spack install -v --dirty mod2c@github %pgi
#need to push the fix to github repos
#spack install --dirty coreneuron@github +report %pgi ^mvapich2
