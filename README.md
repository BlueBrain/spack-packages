# README #

## MAC ##

### BBP Packages ###

```bash
#simulation

spack uninstall -y -f -d -a neuron  %gcc@4.9.3
spack uninstall -y -f -d -a coreneuron
spack uninstall -y -f -d -a nrnh5 ^mpich@3.2 ^hdf5
spack uninstall -y -f -d -a nrnh5 ^mpich@3.2 ^hdf5
spack uninstall -y -f -d -a nrnh5
spack uninstall -y -f -d -a mod2c
spack uninstall -y -f -d -a reportinglib

spack install mod2c %gcc@4.9.3
spack install nrnh5 %gcc@4.9.3 ^mpich@3.2
spack install reportinglib %gcc@4.9.3  ^mpich@3.2
spack install neuron +mpi +hdf5 %gcc@4.9.3 ^mpich@3.2
spack install neurodamus %gcc@4.9.3 ^mpich@3.2
spack install coreneuron +report +hdf5 %gcc@4.9.3 ^mpich@3.2

#petsc
spack -d install --keep-stage -v petsc +mpi +hdf5 %gcc@4.9.3 ^mpich@3.2 ^hdf5 ^python %clang  #installing python with gcc gives same error due to header issues, compile it with clang
```

packages.yaml is simple enough for now:
```bash
$ cat ~/.spack/packages.yaml

packages:
    cmake:
        paths:
            cmake@3.6.1 arch=darwin-elcapitan-x86_64: cmake-3.6.1-gcc-4.9.3-2xoditq
        buildable: False
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

Packages.yaml file as:

```bash
$ cat ~/.spack/packages.yaml
packages:
    intelmpi:
        paths:
            #intelmpi@5.0.1%intel@15.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/impi/5.0.1.035/intel64
            #intelmpi@4.1.1%intel@15.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/impi/4.1.1.036/intel64
            intelmpi@6.0%intel@17.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/2017/compilers_and_libraries_2017.0.098/linux/mpi/intel64/
            #intelmpi@6.0%intel@17.0.0 arch=linux-redhat6-x86_64: intel/compilers_and_libraries_2017.0.098
        buildable: False
    mkl:
        paths:
            mkl@1.0%intel@15.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/mkl
        buildable: False
    cmake:
        paths:
            cmake@3.6.1 arch=linux-redhat6-x86_64: cmake-3.6.1-gcc-4.4.7-xhpqagp
        buildable: False
    mvapich2:
        paths:
            mvapich2@2.0.1 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/tools/mvapich2/mvapich2-2.0.1-nocuda-slurm-14.03.4.2/install
        buildable: False
    autoconf:
        paths:
            autoconf@system: /usr
        buildable: False
        version: [system]
    automake:
        paths:
            automake@system: /usr
        buildable: False
        version: [system]
    pkg-config:
        paths:
            pkg-config@system: /usr
        buildable: False
        version: [system]
    libtool:
        paths:
            libtool@system: /usr
        buildable: False
        version: [system]
#    hdf5:
#        version: [1.8.16]
    all:
        compiler: [gcc, intel@17.0.0, intel@15.0.0]
        providers:
            mpi: [mvapich2, intelmpi]
            blas: [mkl]
            lapack: [mkl]
```

Compiler config as:

```bash
- compiler:
    modules: []
    operating_system: redhat6
    paths:
      cc: /usr/lib64/ccache/gcc
      cxx: /usr/lib64/ccache/g++
      f77: /usr/bin/gfortran
      fc: /usr/bin/gfortran
    spec: gcc@4.4.7
- compiler:
    modules: []
    operating_system: redhat6
    paths:
      cc: /gpfs/bbp.cscs.ch/apps/viz/intel/composer_xe_2015.0.090/bin/intel64/icc
      cxx: /gpfs/bbp.cscs.ch/apps/viz/intel/composer_xe_2015.0.090/bin/intel64/icpc
      f77: /gpfs/bbp.cscs.ch/apps/viz/intel/composer_xe_2015.0.090/bin/intel64/ifort
      fc: /gpfs/bbp.cscs.ch/apps/viz/intel/composer_xe_2015.0.090/bin/intel64/ifort
    spec: intel@15.0.0
- compiler:
    modules: []
    operating_system: redhat6
    paths:
      cc: /gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/opt/spack/linux-redhat6-x86_64/gcc-4.4.7/gcc-4.9.3-hmoqz37cd4wndmpiu3r5vckufbifl5xi/bin/gcc
      cxx: /gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/opt/spack/linux-redhat6-x86_64/gcc-4.4.7/gcc-4.9.3-hmoqz37cd4wndmpiu3r5vckufbifl5xi/bin/g++
      f77: /gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/opt/spack/linux-redhat6-x86_64/gcc-4.4.7/gcc-4.9.3-hmoqz37cd4wndmpiu3r5vckufbifl5xi/bin/gfortran
      fc: /gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/opt/spack/linux-redhat6-x86_64/gcc-4.4.7/gcc-4.9.3-hmoqz37cd4wndmpiu3r5vckufbifl5xi/bin/gfortran
    spec: gcc@4.9.3
- compiler:
    modules: []
    operating_system: redhat6
    paths:
      cc: /gpfs/bbp.cscs.ch/apps/viz/intel/2017/compilers_and_libraries_2017/linux/bin/intel64/icc
      cxx: /gpfs/bbp.cscs.ch/apps/viz/intel/2017/compilers_and_libraries_2017/linux/bin/intel64/icpc
      f77: null
      fc: null
    spec: intel@17.0.0
```
