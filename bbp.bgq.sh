set -e
set -x

spack uninstall -f -a -d -y mod2c
spack uninstall -f -a -d -y nrnh5
spack uninstall -f -a -d -y neuron
spack uninstall -f -a -d -y reportinglib
spack uninstall -f -a -d -y coreneuron
spack uninstall -f -a -d -y neurodamus
spack uninstall -f -a -d -y neuron-nmodl


spack install mod2c %gcc os=redhat6
spack install reportinglib%xl os=CNK ^bgqmpi os=CNK
spack install nrnh5%xl +zlib os=CNK ^bgqmpi
spack install neuron-nmodl%gcc os=redhat6

spack install neuron%xl +mpi +hdf5 +cross-compile os=CNK ^bgqmpi ^neuron-nmodl%gcc os=redhat6 ^nrnh5@develop%xl@12.1+zlib arch=bgq-CNK-ppc64
spack install neurodamus%xl os=CNK ^bgqmpi ^neuron@develop%xl@12.1+hdf5+mpi+python+cross-compile arch=bgq-CNK-ppc64 ^neuron-nmodl%gcc os=redhat6 ^nrnh5@develop%xl@12.1+zlib arch=bgq-CNK-ppc64
spack install coreneuron@master%xl +hdf5 +neurodamus +report os=CNK ^bgqmpi ^mod2c%gcc os=redhat6 ^neurodamus@develop%xl@12.1 arch=bgq-CNK-ppc64 ^neuron@develop%xl@12.1+hdf5+mpi+python+cross-compile arch=bgq-CNK-ppc64 ^neuron-nmodl%gcc os=redhat6 ^nrnh5@develop%xl@12.1+zlib arch=bgq-CNK-ppc64
