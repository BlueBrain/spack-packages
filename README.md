# README #

## MAC ##

### BBP Packages ###

```bash
#sim
spack install mod2c %gcc@4.9.3
spack install reportinglib %gcc@4.9.3  ^mpich@3.2
spack install neuron +mpi +hdf5 %gcc@4.9.3 ^mpich@3.2
spack install neurodamus %gcc@4.9.3 ^mpich@3.2
spack install coreneuron +report +hdf5 %gcc@4.9.3 ^mpich@3.2

#petsc
spack -d install --keep-stage -v petsc +mpi +hdf5 ^mpich@3.2 ^hdf5 ^python %clang  #installing python with gcc gives same error due to header issues, compile it with clang
```

## Lugano ##

### BBP Packages ###

#### Intel ####

```bash
spack install mod2c  %intel@15.0.0
spack install nrnh5 %intel@15.0.0 ^intelmpi
spack install neuron +mpi +hdf5 %intel@15.0.0 ^intelmpi
spack install reportinglib %intel@15.0.0 ^intelmpi
spack install neurodamus %intel@15.0.0 ^intelmpi
spack install coreneuron +report +hdf5 %intel@15.0.0 ^intelmpi
```

```bash
$ cat ~/.spack/packages.yaml
packages:
    intelmpi:
        version: [5.0.1]
        paths:
            intelmpi@5.0.1%intel@15.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/impi/5.0.1.035/intel64
        buildable: False
    mkl:
        version: [1.0]
        paths:
            mkl@1.0%intel@15.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/mkl/
        buildable: False
    all:
        compiler: [intel@15.0.0]
        providers:
            mpi: [intelmpi]
            blas: [mkl]
            lapack: [mkl]
```