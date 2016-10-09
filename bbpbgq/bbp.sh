#!/bin/bash
#SBATCH --job-name="build"
#SBATCH --time=2:00:00
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --account=proj16
#SBATCH --exclusive


spack uninstall -f -a -d -y mod2c
spack uninstall -f -a -d -y nrnh5
spack uninstall -f -a -d -y neuron
spack uninstall -f -a -d -y reportinglib
spack uninstall -f -a -d -y coreneuron
spack uninstall -f -a -d -y neurodamus
spack uninstall -f -a -d -y neuron-nmodl

set -e

spack install mod2c os=redhat6
spack install reportinglib ^mpich
spack install nrnh5 +zlib ^mpich
spack install neuron +mpi +cross-compile ^mpich ^neuron-nmodl os=redhat6
spack install neurodamus ^neuron+mpi+cross-compile ^mpich ^neuron-nmodl os=redhat6
spack install coreneuron +hdf5 +neurodamus +report ^mpich ^mod2c os=redhat6 ^neurodamus ^neuron+mpi+cross-compile ^neuron-nmodl os=redhat6 ^nrnh5+zlib
