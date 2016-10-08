set -e
set -x

spack uninstall -f -a -d -y mod2c
spack uninstall -f -a -d -y nrnh5
spack uninstall -f -a -d -y neuron
spack uninstall -f -a -d -y reportinglib
spack uninstall -f -a -d -y coreneuron
spack uninstall -f -a -d -y neurodamus
spack uninstall -f -a -d -y neuron-nmodl

spack install mod2c os=SuSE11
spack install reportinglib ^craympi
spack install nrnh5 +zlib ^craympi

spack install -v coreneuron%intel +hdf5 ~neurodamus +report ^craympi os=CNL ^nrnh5+zlib%intel os=CNL ^mod2c%gcc os=SuSE11

exit 0

#still doesnt work
spack install neuron +mpi +cross-compile ^craympi ^neuron-nmodl os=SuSE11
spack install neurodamus ^neuron+mpi+cross-compile ^craympi ^neuron-nmodl os=SuSE11
spack install coreneuron +hdf5 +neurodamus +report ^craympi ^mod2c os=SuSE11 ^neurodamus ^neuron+mpi+cross-compile ^neuron-nmodl os=SuSE11 ^nrnh5+zlib

#also works
spack install -v coreneuron%intel +hdf5 ~neurodamus +report ^mpich@7.2.2 os=CNL ^nrnh5+zlib%intel os=CNL ^mod2c%gcc os=SuSE11
