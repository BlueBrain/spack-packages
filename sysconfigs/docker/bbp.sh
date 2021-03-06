spack uninstall -y -f -d -a neuron
spack uninstall -y -f -d -a coreneuron
spack uninstall -y -f -d -a nrnh5
spack uninstall -y -f -d -a nrnh5
spack uninstall -y -f -d -a mod2c
spack uninstall -y -f -d -a reportinglib
spack uninstall -y -f -d -a neurodamus

set -e
set -x

spack install mpich %gcc
spack install hdf5 +mpi
spack install python

spack install mod2c %gcc
spack install nrnh5 %gcc ^mpich

spack install reportinglib %gcc  ^mpich

spack install neuron@develop +mpi %gcc ^mpich
spack install neuron@hdf +mpi %gcc ^mpich

spack install neurodamus@master +compile %gcc ^mpich
spack install neurodamus@develop +compile %gcc ^mpich
spack install neurodamus@hdf +compile %gcc ^mpich

spack install coreneuron@develop +report %gcc ^mpich
spack install coreneuron@hdf +report %gcc ^mpich
