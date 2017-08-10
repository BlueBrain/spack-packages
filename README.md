# Getting Started With Spack #

If you are first time here and never used Spack then may be you are interested in:

* [Spack tutorial (SperComputing 2016) ](http://spack.readthedocs.io/en/latest/tutorial.html)
* [Spack Documentation](http://spack.readthedocs.io/en/latest/#)
* [Spack Google Group Discussion](https://groups.google.com/forum/#!forum/spack)
* And [Spack Slack Channel](https://spackpm.slack.com/messages/C5W7NKZJT/)

Otherwise,

This document describes basic steps required to start development environment with Spack. Even though Spack can build entire software stack from scratch, for the developers it is more convenient to bootstrap from the existing packages provided by system which could be your personal laptop or HPC cluster. Hence, following instructions are divided into  platform `independnet` and platform `specific` settings.

## Platform Independent Settings ##

These steps are independent of any platform i.e. you have to do this if you want start from scratch or bootstrap from exisiting packages.

#### Prefix ####
We will use following prefix throughout the scripts. Set those according to your convenience:

```bash
export SOURCE_HOME_DIR=$HOME/workarena/software/sources
```


#### Clone Reository ####
Clone spack repository from Github. You can use [official repository](https://github.com/LLNL/spack) from LLNL but I am adding few modifications / workarounds for exisiting bugs and other systems like Lugano bg-q / vizcluster.

```bash
cd $SOURCE_HOME_DIR
git clone https://github.com/pramodskumbhar/spack.git

# if you want to track upstream development branch
cd spack
git remote add llnl https://github.com/llnl/spack.git
```

#### Additional Packages ####

NEURON and CoreNEURON related packages are maintained in separate repository. In order to build those packages with Spack, add bellow github repository as Spack repository:

```bash
cd $SOURCE_HOME_DIR
git clone https://github.com/pramodskumbhar/spack-packages.git
spack repo add --scope site `pwd`/spack-packages
```

Make sure to update / pull both repositories if there are any upstream changes.


#### Update .bashrc or .bash_profile ####
In order to access spack shell support, add following in your `.bashrc` (linux) or `.bash_profile` (OS X) : 

```bash
export SPACK_ROOT=$HOME/workarena/software/sources/spack
export PATH=$SPACK_ROOT/bin:$PATH
source $SPACK_ROOT/share/spack/setup-env.sh
```

We assume that the `module` command is already installed/avaialble on the system. Check Spack documentation if this is not the case.

## Platform Specific Configuration ##

Here are the instructions to get started on Mac, Linux, Lugano VizCluster and Lugano BG-Q System. Instructions for Cray system (like BlueWater, TITAN and Theta) will be added later.

The configurations are present in `spack-configs` repository in btbucket:

```bash
cd $SOURCE_HOME_DIR
git clone https://github.com/pramodskumbhar/spack-configs.git
```

Typically we will copy platform specific configurations to your `$HOME/.spack` directory. For example, on lugano vizcluster we do:

```
mkdir -p $HOME/.spack/linux/
cp -r spack-configs/bbpviz/* ~/.spack/linux/
```

The `config.yaml` (`$HOME/.spack/linux/config.yaml` here) file typically looks like :

```
config:
  install_tree: /gpfs/bbp.cscs.ch/project/proj16/$user/SPACK_INSTALL/viz/simulation/install
  module_roots:
    tcl: /gpfs/bbp.cscs.ch/project/proj16/$user/SPACK_INSTALL/viz/simulation/modules

```

These are paths where packages will be installed and modules will be automatically generated. Update these paths as per your setting and make sure to add `module_roots` path to `MODULEPATH` so that `spack load` will find those:

```
export MODULEPATH=/gpfs/bbp.cscs.ch/project/proj16/kumbhar/SPACK_INSTALL/viz/simulation/modules:$MODULEPATH
```

> Note that if `$user` present in the path then replace it with your username i.e. $USER


#### Mac OS X ###
We can build entire software stack including `CMake`, `GCC`, `LLVM`, `MPI` (`MPICH` or `OpenMPI`) with Spack on our laptop. But for the development purpose, most of the time, we don't want to build these packages from source as they take long time to build. In this case it is goood idea to use `Homebrew` or `Macport` to install these pakages. Note that you can skip installing packages from `Homebrew` if you want to install everything from source with Spack. But then you will end up building lots of dependencies.

So lets start installing common packages that we need:

```bash
brew install autoconf automake libtool pkg-config cmake flex bison
```

Apart from Apple Clang, we may want to use `GNU`:

```bash
brew install gcc49
```

If you want, for convenience, create symlinks for gcc, g++ and fortran (this is because default gcc and g++ are actually clang compilers on OSX).

```bash
cd /usr/local/bin/
ln -s ../Cellar/gcc\@4.9/4.9.4/bin/g++-4.9 g++
ln -s ../Cellar/gcc\@4.9/4.9.4/bin/gcc-4.9 gcc
ln -s ../Cellar/gcc\@4.9/4.9.4/bin/gfortran-4.9 fortran
```


For Zlib

```bash
brew tap homebrew/dupes
brew install zlib
```

We commonly need MPI library, we can install it using `Homebrewa`. The `openmpi` library installed using `Homebrew` can be used with other compilers (gcc/clang):

```
brew install openmpi
```

Spack uses `environment-module` i.e. `Modules` and `Lmod` packages to load / unload modules. You can install those using Spack or from `Homebrew` :

```bash
brew install modules lmod
```

If you are using parallel HDF5, install it using:

```bash
 brew install hdf5 --with-mpi
```

Now we have all required packages installed from `Homebrew`. Update `.bashrc_profile` with path for `modules` package so that Spack can use it:

```bash
MODULES_HOME=`brew --prefix modules`
source ${MODULES_HOME}/Modules/init/bash
```

Or, if you want to use more advanced hierarchical module environemnt based on `Lmod` then:

```bash
LMOD_HOME=`brew --prefix lmod`
source $LMOD_HOME/lmod/init/bash
```

Lets start with Spack now!

#### Compielr Configuration ####

First step with Spack is to find compilers available on system. We can do this with following command:

``` bash
spack compiler find
```

This will find common compilers available in `$PATH` and print out the list:

``` bash
==> Added 2 new compilers to /Users/kumbhar/.spack/darwin/compilers.yaml
    gcc@4.9.4  clang@8.1.0-apple
==> Compilers are defined in the following files:
    /Users/kumbhar/.spack/darwin/compilers.yaml
```

Note that new file `.spack/darwin/compilers.yaml` is created in `$HOME` which stores all compiler configuration. This file looks like :

``` bash
compilers:
- compiler:
    environment: {}
    extra_rpaths: []
    flags: {}
    modules: []
    operating_system: sierra
    paths:
      cc: !!python/unicode '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang'
      cxx: !!python/unicode '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++'
      f77: /usr/local/bin/gfortran
      fc: /usr/local/bin/gfortran
    spec: clang@8.1.0-apple
    target: x86_64
- compiler:
    environment: {}
    extra_rpaths: []
    flags: {}
    modules: []
    operating_system: sierra
    paths:
      cc: /usr/local/bin/gcc-4.9
      cxx: /usr/local/bin/g++-4.9
      f77: /usr/local/bin/gfortran-4.9
      fc: /usr/local/bin/gfortran-4.9
    spec: gcc@4.9.4
    target: x86_64
```

The `compilers.yaml` file has configuration for every compiler. Note that fortran compilers are *not* provided by `Clang` compiler and hence building any package requiring fortran compiler will fail with `Clang` (for example, `hdf5` package). It's safe to use `gfortran` with `clang` compilers (until we get `flang` releases in near future).

You can litst the compilers using `spack compilers` :

``` bash
spack compilers
==> Available compilers
-- clang sierra-x86_64 ------------------------------------------
clang@8.1.0-apple

-- gcc sierra-x86_64 --------------------------------------------
gcc@4.9.4
```

And if you install new compiler, then force to re-search it using:

```bash
spack compiler find

==> Found no new compilers
```

Often compilers are installed in non-standard directories which are not in $PATH. You can provide path searc compilers as:

```bash
spack compiler find /usr/local/Cellar/llvm/3.9.0/

==> Added 1 new compiler to /Users/kumbhar/.spack/darwin/compilers.yaml
   clang@3.9.0
```


#### Package Configuration ####

Second important step is to tell spack about `existing` packages. Spack can build most of the environment for you but we want to use packages like `MPI`, `CMake`, `autotools` etc. provided by the system. This is more important on HPC facilities where packages like `MPI` are tuned for hardware and provided by speromputing centre/vendors. We don't want to install those ourself from source. This is where `packages.yaml` file in `$HOME/.spack/darwin/` comes into action (`darwin` here is platform name). The `packages.yaml` tells spack which existing packages to use, their versions, compiler preferences etc. For example, if you try to build package which need `CMake`, Spack will try to build `CMake` and all its dependencies from source. But we have previously installed `CMake` with `brew` and we can tell spack to use it using below `packages.yaml` :

```bash
packages:
    cmake:
        paths:
            cmake@3.8.2: /usr/local
        buildable: False
        version: [3.8.2]
```

In the above configuration we told Spack to use `CMake` from `/usr/local` (installed by `Homebrew`). Finally `buildable: False` tells Spack to not build this package from source. So Spack will never try to build this package explicitly and if constraints are not satisfied, it give error like :

```bash
==> Error: The spec 'cmake' is configured as not buildable, and no matching external installs were found
```

When we specify dependency like `depends_on('cmake', type='build')`, Spack will match any cmake version available. But many packages specify version constraints in the dependency like `depends_on('cmake@2.8.12:', type='build')`. This indicate that `CMake` version should be  `>=2.8.12`. To satisfiy this constraint you have to make sure to provide appropriate version. Otherwise you can remove `buildable: False` option.

We can provide preferences for all packages in `packages.yaml`. For example, in the below configuration we specified compiler preferences for building any package. Also, we specify `mpich` as `MPI` provider.

```bash
   all:
       compiler: [gcc@4.9.3, clang@7.3.0-apple]
       providers:
           mpi: [mpich]
```

Another important aspect is `variants`. The `packages.yaml` allows us to specify `variant` preferences. This is important aspect while building packages on different platforms or by different members of the team. For example, consider the example of `HDF5` package. If you look at `HDF5` package using `spack info`, it shows different variants including `fortran` :

```bash
spack info hdf5
Package:    hdf5
Homepage:   http://www.hdfgroup.org/HDF5/
....
Variants:
   Name          Default   Description

   cxx           on        Enable C++ support
   debug         off       Builds a debug version of the library
   fortran       on        Enable Fortran support
....
```

On OS X if you dont have fortran compilers with `llvm` toolchain, you can disable fortran variant in `packages.yaml` as:

```bash
   hdf5:
       variants: ~fortran
```

With the above configuration we tell spack to not build fortan bindings of `HDF5` package. Now `HDF5` will be built by `Clang` compiler without any errors. Similarly we can specify version preferences. For example, latest `Boost` version takes long time to build. We need `Boost` for testing purpose and old version is sufficient for us:

```bash
   boost:
       version: [1.51.0]
```

> Note that older version of Spack allowed to specify version as `system`. This means the version specified is provided by `system` and use it without checking version requirements. It is now recommended to specify exact version number in `packages.yaml` to avoid incompatible version issues.

With all system packages, `$HOME/.spack/darwin/packages.yaml` looks like below:

```bash
packages:
    gcc:
        paths:
            gcc@4.9.4%gcc@4.4: /usr/local
        buildable: False
        version: [4.9.4]

    llvm:
        paths:
            llvm@8.1.0-apple%gcc@4.4: /usr/local
        buildable: False
        version: [8.1.0-apple]

    cmake:
        paths:
            cmake@3.8.2: /usr/local
        buildable: False
        version: [3.8.2]

    autoconf:
        paths:
            autoconf@system: /usr/local
        buildable: False
        version: [system]

    automake:
        paths:
            automake@system: /usr/local
        buildable: False
        version: [system]

    libtool:
        paths:
            libtool@system: /usr/local
        buildable: False
        version: [system]

    openssl:
        paths:
            openssl@system: /usr/local
        buildable: False
        version: [system]

    flex:
        paths:
            flex@system: /usr/local
        buildable: False
        version: [system]

    bison:
        paths:
            bison@system: /usr/local
        buildable: False
        version: [system]

    pkg-config:
        paths:
            pkg-config@0.29.2%clang@8.1.0-apple: /usr/local
            pkg-config@0.29.2%gcc@4.9.4: /usr/local
        buildable: False
        version: [0.29.1]

    environment-modules:
        paths:
            environment-modules@system: /usr/local
        buildable: False
        version: [system]

    python:
        paths:
            python@2.7.10: /System/Library/Frameworks/Python.framework/Versions/2.7
        buildable: False
        version: [2.7.10]

    hdf5:
        paths:
            hdf5@1.8.17: /usr/local
        buildable: False
        variants: ~fortran
        version: [1.8.17]

    zlib:
        paths:
            zlib@1.2.8: /usr/local
        buildable: False
        version: [1.2.8]

    qt:
        paths:
            qt@5.5.1: /usr/local/Cellar/qt55/5.5.1
        buildable: False
        version: [5.5.1]

    mpich:
        paths:
            mpich@3.2%gcc@4.9.4: /usr/local
            mpich@3.2%clang@8.1.0-apple: /usr/local

        buildable: False
        version: [3.2]

    boost:
        version: [1.51.0]

    tau:
        variants: ~openmp ~comm ~phase

    coreneuron:
        variants: ~openmp

    all:
        compiler: [gcc@4.9.3, clang@8.1.0-apple]
        providers:
            mpi: [mpich]
```

With above configuration we tell Spack to find various packages under `/usr/local` installed by `Homebrew`, compiler preferences and `mpich` as `MPI` library preference. Note that we have specified version `3.2` for `mpich` because some packages can request support for specific `MPI` standard (1, 2, 3). 

#### Spack Configurations ####

You can find spack configurations for different systems [here](https://github.com/pramodskumbhar/spack-configs).

#### Spack in Action : Installing Packages ####

Now we have setup everything we needed to start installing our development packages!
We have added `spack-packages` package repository in the beginning. You can see which `package` repository we have added using :

```bash
$ spack repo list

2 package repositories.
spack-packages        /Users/kumbhar/workarena/software/sources/spack-packages
builtin    /Users/kumbhar/workarena/software/sources/spack/var/spack/repos/builtin
```

Now you can list available packages using `spack list` command :

```bash
$ spack list *neuron*

==> 3 packages.
coreneuron  neuron  neuron-nmodl

$ spack list mod2c

==> 1 packages.
mod2c
```

We can see the dependencies of `mod2c` package with `spack spec`:

```bash
$ spack spec mod2c
Input spec
--------------------------------
mod2c

Normalized
--------------------------------
mod2c
    ^cmake@2.8.12:

Concretized
--------------------------------
mod2c@develop%clang@8.1.0-apple arch=darwin-sierra-x86_64
    ^cmake@3.8.2%clang@8.1.0-apple~doc+ncurses+openssl+ownlibs~qt arch=darwin-sierra-x86_64
```

The `Concretized ` section gives final dependency list. Before actual installing package, we can use `-I` option to see which components are already installed :

```bash
$spack spec -I petsc
Input spec
--------------------------------
     petsc

Normalized
--------------------------------
     petsc
         ^blas
         ^lapack
         ^python@2.6:2.8
             ^bzip2
             ^ncurses
                 ^pkg-config
             ^openssl
                 ^zlib
             ^readline
             ^sqlite

Concretized
--------------------------------
     petsc@3.7.6%clang@8.1.0-apple+boost~complex~debug+double+hdf5+hypre~int64+metis+mpi~mumps+shared+superlu-dist~trilinos arch=darwin-sierra-x86_64
[+]      ^hdf5@1.8.17%clang@8.1.0-apple+cxx~debug~fortran+mpi+pic+shared~szip~threadsafe arch=darwin-sierra-x86_64
         ^hypre@2.11.2%clang@8.1.0-apple~int64~internal-superlu~shared arch=darwin-sierra-x86_64
[+]          ^mpich@3.2%clang@8.1.0-apple+hydra+pmi+romio~verbs arch=darwin-sierra-x86_64
             ^openblas@0.2.19%clang@8.1.0-apple~openmp+pic+shared arch=darwin-sierra-x86_64
         ^metis@5.1.0%clang@8.1.0-apple~debug~gdb~int64~real64+shared arch=darwin-sierra-x86_64
[+]          ^cmake@3.8.2%clang@8.1.0-apple~doc+ncurses+openssl+ownlibs~qt arch=darwin-sierra-x86_64
         ^parmetis@4.0.3%clang@8.1.0-apple~debug~gdb+shared arch=darwin-sierra-x86_64
[+]      ^python@2.7.10%clang@8.1.0-apple~shared~tk~ucs4 arch=darwin-sierra-x86_64
         ^superlu-dist@5.1.3%clang@8.1.0-apple~int64 arch=darwin-sierra-x86_64
```

Packages indicated with `[+]` are already installed. As `CMake` is specified in `packages.yaml`, Spack indicates the package is installed and won't build it again. 

We can install `mod2c` package as:

```bash
$ spack install mod2c
==> Installing mod2c
==> cmake is externally installed in /usr/local
==> Trying to fetch from file:///Users/kumbhar/workarena/software/sources/spack/var/spack/cache/mod2c/mod2c-develop.tar.gz
curl: (37) Couldn't open file /Users/kumbhar/workarena/software/sources/spack/var/
........
==> Trying to clone git repository:
 ssh://bbpcode.epfl.ch/sim/mod2c
Cloning into 'mod2c'...
remote: Counting objects: 124, done
....
==> No patches needed for mod2c
==> Building mod2c
==> Successfully installed mod2c
 Fetch: 4.07s.  Build: 14.35s.  Total: 18.43s.
[+] /Users/kumbhar/workarena/software/sources/spack/opt/spack/darwin-elcapitan-x86_64/gcc-4.9.3/mod2c-develop-3m7yiug24mfy677krgwgstsue6hmnrr4
```

You can use different compiler or version of the package during installation:

```bash
$ spack install mod2c %clang           #use clang
```

You can find installed packages usinf `spack find` as:

```bash
$ spack find mod2c

==> 3 installed packages.
-- darwin-elcapitan-x86_64 / clang@7.3.0-apple ------------------
mod2c@github
-- darwin-elcapitan-x86_64 / gcc@4.9.3 --------------------------
mod2c@github  mod2c@develop
```

You can now install required packages one by one or write some script to install packages with different combinations. Here example of installing all stack with `Clang` and `GNU` compiler :

```bash
#!/bin/bash

set -x

#### LIST OF PACKAGES ####
dev_packages=(
    'neuronperfmodels@neuron ^reportinglib+static'
    'coreneuron@perfmodels +report ^reportinglib+static'
    'neuronperfmodels@neuron +profile ^reportinglib+static'
    'coreneuron@perfmodels +profile +report ^reportinglib+static'
)

compilers=(
    '%gcc'
    '%clang'
)

##### UNINSTALL PACKAGE #####
uninstall_package() {
	for package in "${dev_packages[@]}"
    do
	    spack uninstall -a -f -R -y $package
	done
}

#if any inconsistent packages
spack reindex

# uninstall all packages
uninstall_package

# stop if iany package installation fails
set -e

# TAU profiler options
export TAU_OPTIONS='-optPDTInst -optNoCompInst -optRevert -optPdtCOpts="-D_CRAYC=1" -optTauSelectFile=~/spack-configs/nrnperfmodels.tau'

# for every compiler, build each package
for compiler in "${compilers[@]}"
do
	for package in "${dev_packages[@]}"
    do
        spack install $package $compiler
    done
done

```


#### Lugano Vizcluster ###

All above instructions for OS X platform will be useful to setup development environment on Lugano Vizcluster, read those first. We list few important exceptions that we must have to consider :

* On HPC cluster system like `Lugano Vizcluster`, we dont want to / should not install compilers, MPI libraries etc.
* We should use existing modules as much as possible.
* Spack discourage use of `LD_LIBRARY_PATH` from user space. Many existing modules on HPC systems set `LD_LIBRARY_PATH`. In order to use these modules, we have to use `--dirty` flag during installation (related issue has been reported upstream).
* All `MPI` packages are externally installed. The actual libraries are `mvapich2`, `mpich3`, `intelmpi` etc. Many times we have to specify these `MPI` libraries explicitly on command line with `install` or `spec` command like `spack spec neuron +mpi ^mvapich2` otherwise we get `list out of index` error. (this is likely a bug and has been reported upstream).
* I have used packages like `autotools`, `pkg-config` from `/usr/bin/` which is discouraged! As these are only used for building, I have never seen any issues (if versions are properly specified). I am using those in `packages.yaml` to quickly bootstrap without building too many packages. But it's may not be good idake sure to copy up to date version from `bbpviz` directory as:

Make sure to copy up to date version from `bbpviz` directory as:

```
mkdir -p $HOME/.spack/linux
cp -r bbpviz/* $HOME/.spack/linux/
```

The configuration looks like:

```bash
packages:
    intelmpi:
        paths:
            intelmpi@develop: /gpfs/bbp.cscs.ch/apps/viz/intel/2017/compilers_and_libraries_2017.0.098/linux/mpi/intel64
        version: [develop]
        buildable: False
    cmake:
        paths:
            cmake@3.6.2: /gpfs/bbp.cscs.ch/apps/viz/bbp/dev/cmake/3.6.2
        version: [3.6.2]
        buildable: False
    mvapich2:
        modules:
            mvapich2@2.0.1%gcc@4.9.0: mvapich2/2.0.1-nocuda
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
            pkg-config@0.29.1: /usr
        buildable: False
        version: [0.29.1]
    libtool:
        paths:
            libtool@system: /usr
        buildable: False
        version: [system]
    python:
        paths:
            python@2.6.6: /usr
        version: [2.6.6]
        buildable: False
    cuda:
        modules:
            cuda@6.0: cuda/6.0
        version: [6.0]
        buildable: False
    mpich:
        modules:
            mpich@3.2: pgi/mpich/16.5
        buildable: False
        version: [3.2]
    hdf5:
        paths:
            hdf5@1.10.0%gcc@4.9.0: /gpfs/bbp.cscs.ch/project/proj16/software/viz/hpc/hdf5-gcc
            hdf5@1.10.0%intel@17.0.0: /gpfs/bbp.cscs.ch/project/proj16/software/viz/hpc/hdf5-icc
            hdf5@1.8.5%pgi@16.5-0: /gpfs/bbp.cscs.ch/project/proj16/software/viz/hpc/hdf5-pgi
        variants: ~fortran ~shared ~cxx
        buildable: False
        version: [1.10.0]
    zlib:
        paths:
            zlib@1.2.8%gcc@4.9.0: /gpfs/bbp.cscs.ch/project/proj16/software/viz/hpc/zlib-gcc
            zlib@1.2.8%intel@17.0.0: /gpfs/bbp.cscs.ch/project/proj16/software/viz/hpc/zlib-icc
            zlib@1.2.8%pgi@16.5-0: /gpfs/bbp.cscs.ch/project/proj16/software/viz/hpc/zlib-pgi
        buildable: False
        version: [1.2.8]

    tau:
        variants: ~openmp ~comm ~phase

    coreneuron:
        variants: ~openmp

    all:
        compiler: [gcc@4.9.0, intel@17.0.0]
        providers:
            mpi: [mvapich2, intelmpi, mpich]
```

And build script for `Intel`, `PGI` and `GNU` compiler looks like : 

```bash

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
   spack install --dirty nrnh5@develop $compiler_mpi

   spack install --dirty neuron@develop +mpi $compiler_mpi
   spack install --dirty neuron@hdf +mpi $compiler_mpi

   spack install --dirty reportinglib $compiler_mpi

   spack install --dirty neurodamus@master +compile $compiler_mpi
   spack install --dirty neurodamus@develop +compile $compiler_mpi
   spack install --dirty neurodamus@hdf +compile $compiler_mpi

   spack install --dirty coreneuron@develop +report $compiler_mpi
   spack install --dirty coreneuron@github +report $compiler_mpi
   spack install --dirty coreneuron@hdf +report $compiler_mpi
done

spack install --dirty mod2c@develop %pgi
spack install --dirty coreneuron@develop +report %pgi ^mvapich2

spack install --dirty mod2c@github %pgi
#need to push the fix to github repos
#spack install --dirty coreneuron@github +report %pgi ^mvapich2
```


#### Lugano BG-Q Configuration ##

Note that up to date configurations are under `bbpbgq/` directory. Make sure to copy those as:

```
mkdir -p $HOME/.spack/bgq/
cp bbpbgq/* $HOME/.spack/bgq/
```

#### Piz Daint Configuration ####

Note that up to date configurations are under `daint/` directory. Make sure to copy those as:

```
mkdir -p $HOME/.spack/cray/
cp daint/* $HOME/.spack/cray/
```

The instructions / scrit to install NEURON/CoreNEURON is provided under `daint/bbp.sh`.

Also I have been updating Spack with the latest upstream changes from LLNL repository. I have created new branch called `upstream` which should be used on Cray platforms. It should work on lugano/mira but I just tested it on Piz Daint. So make sure to clone this new branch on Piz Daint.

```
cd spack
git checkout upstream
```

#### Theta Configuration ####

Note that up to date configurations are under `theta/` directory. Make sure to copy those as:

```
mkdir -p $HOME/.spack/cray/
cp theta/* $HOME/.spack/cray/
```

The instructions / scrit to install NEURON/CoreNEURON is provided under `theta/bbp.sh`.

Similar to piz-daint make sure to use `upstream` branch of spack.
```
cd spack
git checkout upstream
```


## Generating Modules ##

Here are brief instructions how we generate module on OS X with `modules.yaml` provided in this repository.

You can install `lmod` via spack but it's better to install as system package.

```
brew install lmod
```

Then activate `lmod` as:

```bash
LMOD_HOME=`brew --prefix lmod`
source $LMOD_HOME/lmod/init/bash
```

> `LMOD_HOME` on OS X is `/usr/local/opt/lmod`

Assuming you have proper `modules.yaml`, we can generate `lmod` modules with Spack as:

```
spack module refresh --delete-tree -y -m lmod
```

Make sure to set `MODULEPATH` to the `Core` directory :

```bash
export MODULEPATH=/Users/kumbhar/workarena/software/sources/spack/share/spack/lmod/darwin-sierra-x86_64/Core/
```

Now `module av` should show you packages built with core compilers:

```bash
$ module av

 /Users/kumbhar/workarena/software/sources/spack/share/spack/lmod/darwin-sierra-x86_64/Core
   gcc/4.9.4    llvm/8.1.0-apple (L)

  Where:
   L:  Module is loaded
```

Loading one of the compiler will show the modules built with that compiler :

```
$ module av

 /Users/kumbhar/workarena/software/sources/spack/share/spack/lmod/darwin-sierra-x86_64/gcc/4.9.4
   mod2c/develop    neurodamus/develop             python/2.7.10
   mpich/3.2        neuronperfmodels/coreneuron

 /Users/kumbhar/workarena/software/sources/spack/share/spack/lmod/darwin-sierra-x86_64/Core
   gcc/4.9.4 (L)    llvm/8.1.0-apple

  Where:
   L:  Module is loaded
```

And loading `mpich` will show modules compiled with MPI:

```
$ module load mpich/3.2

$ module av

 /Users/kumbhar/workarena/software/sources/spack/share/spack/lmod/darwin-sierra-x86_64/mpich/3.2-xboj7as/gcc/4.9.4
   coreneuron/perfmodels-profile          neuronperfmodels/neuron      (D)
   coreneuron/perfmodels           (D)    reportinglib/develop-profile
   neuron/master-profile                  reportinglib/develop         (D)
   neuron/master                   (D)    tau/2.25.2
   neuronperfmodels/neuron-profile

 /Users/kumbhar/workarena/software/sources/spack/share/spack/lmod/darwin-sierra-x86_64/gcc/4.9.4
   mod2c/develop        neurodamus/develop             python/2.7.10
   mpich/3.2     (L)    neuronperfmodels/coreneuron

 /Users/kumbhar/workarena/software/sources/spack/share/spack/lmod/darwin-sierra-x86_64/Core
   gcc/4.9.4 (L)    llvm/8.1.0-apple

  Where:
   L:  Module is loaded
   D:  Default Module

```

We can now load modules :

```
$ module load neurodamus/develop mod2c/develop
$ module list
Currently Loaded Modules:
  1) gcc/4.9.4   2) mpich/3.2   3) neurodamus/develop   4) mod2c/develop
```

If we swap compilers then previously modules should be swapped automaticaly:

```
$ module swap gcc llvm

Due to MODULEPATH changes, the following have been reloaded:
  1) mod2c/develop     2) mpich/3.2     3) neurodamus/develop
```

Similarly the instructions for modules :

```
MODULES_HOME=`brew --prefix modules`
source ${MODULES_HOME}/Modules/init/bash

export MODULEPATH=/Users/kumbhar/workarena/software/sources/spack/share/spack/modules/darwin-sierra-x86_64/

spack module refresh --delete-tree -y -m tcl
```

And `module av` should shows available modules:

```
$ module av

 /Users/kumbhar/workarena/software/sources/spack/share/spack/modules/darwin-sierra-x86_64/
 coreneuron/perfmodels-clang-mpich
 coreneuron/perfmodels-clang-mpich-profile
 coreneuron/perfmodels-gcc-mpich
 coreneuron/perfmodels-gcc-mpich-profile
 mod2c/develop-clang
 mod2c/develop-gcc
 mpich/3.2-clang
 mpich/3.2-gcc
 neurodamus/develop-clang
 neurodamus/develop-gcc
 neuron/master-clang-mpich
 neuron/master-clang-mpich-profile
 neuron/master-gcc-mpich
 neuron/master-gcc-mpich-profile
 neuronperfmodels/coreneuron-clang
 neuronperfmodels/coreneuron-gcc
 ....
```
