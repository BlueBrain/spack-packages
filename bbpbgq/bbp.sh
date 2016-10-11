#!/bin/bash
#SBATCH --job-name="build"
#SBATCH --time=2:00:00
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --account=proj16
#SBATCH --exclusive

#nmodl is still issue

#uninstall all packages
spack uninstall -f -a -d -y mod2c
spack uninstall -f -a -d -y nrnh5
spack uninstall -f -a -d -y reportinglib
spack uninstall -f -a -d -y neuron-nmodl
spack uninstall -f -a -d -y neuron
spack uninstall -f -a -d -y coreneuron
spack uninstall -f -a -d -y neurodamus

set -e

spack install mod2c os=redhat6
spack install nrnh5 +zlib ^mpich
spack install reportinglib ^mpich
spack install neuron-nmodl os=redhat6
spack install neuron +mpi +hdf5 +cross-compile ^mpich ^neuron-nmodl os=redhat6
spack install neurodamus +compile ^mpich
spack install neurodamus@coreneuronsetup +compile ^mpich
spack install coreneuron +neurodamus +report ^mpich ^mod2c os=redhat6 ^neurodamus
spack install coreneuron@develop +neurodamus +report ^mpich ^nrnh5+zlib ^mod2c os=redhat6
