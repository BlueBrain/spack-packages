#!/bin/bash
#SBATCH --job-name="build"
#SBATCH --time=2:00:00
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --account=proj16
#SBATCH --exclusive

set -e

#gcc
#spack install gcc %gcc
#start using gcc
#spack load gcc
#spack compiler find

export IFORTCFG=$HOME/spackconfig/bbpviz/cfg/ifort.cfg
export ICPCCFG=$HOME/spackconfig/bbpviz/cfg/icc.cfg
export ICCCFG=$HOME/spackconfig/bbpviz/cfg/icc.cfg

#uninstall all packages
#spack uninstall -a -f -d -y hdf5
spack uninstall -y -f -d -a neuron
spack uninstall -y -f -d -a coreneuron
spack uninstall -y -f -d -a nrnh5
spack uninstall -y -f -d -a mod2c
spack uninstall -y -f -d -a reportinglib
spack uninstall -y -f -d -a neurodamus
spack uninstall -y -f -d -a neuron-nmodl

#install hdf5, HDF5 execute some tests which causes libimf.so error
spack install hdf5 +mpi %gcc ^mvapich2
module load intel/compilers_and_libraries_2017.0.098
spack install --dirty hdf5 +mpi %intel ^intelmpi
module purge all

spack reindex

compiler_with_mpi=(
    '%gcc ^mvapich2'
    '%intel ^intelmpi'
)

#serial
spack install mod2c %intel
spack install mod2c %gcc

for compiler_mpi in "${compiler_with_mpi[@]}"
do
    spack install nrnh5 $compiler_mpi
    spack install neuron +mpi +hdf5 $compiler_mpi
    spack install reportinglib $compiler_mpi
    spack install neurodamus $compiler_mpi
    spack install coreneuron +report +hdf5 $compiler_mpi
done
