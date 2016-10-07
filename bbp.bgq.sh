set -e
set -x

spack uninstall -f -a -d -y mod2c
spack uninstall -f -a -d -y nrnh5
spack uninstall -f -a -d -y neuron
spack uninstall -f -a -d -y reportinglib
spack uninstall -f -a -d -y coreneuron
spack uninstall -f -a -d -y neurodamus
spack uninstall -f -a -d -y neuron-nmodl

spack install mod2c os=redhat6
spack install reportinglib ^bgqmpi
spack install nrnh5 +zlib ^bgqmpi

spack install neuron +mpi +cross-compile ^bgqmpi ^neuron-nmodl os=redhat6
spack install neurodamus ^neuron+mpi+cross-compile ^bgqmpi ^neuron-nmodl os=redhat6
spack install coreneuron +hdf5 +neurodamus +report ^bgqmpi ^mod2c os=redhat6 ^neurodamus ^neuron+mpi+cross-compile ^neuron-nmodl os=redhat6 ^nrnh5+zlib
