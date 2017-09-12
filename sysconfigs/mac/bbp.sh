#!/bin/bash

# PLATFORM SPECIFIC NOTES ::
# on os-x there few issues while using tau with coreneuron. I have seen below error:
#   "/usr/local/Cellar/gcc49/4.9.3/lib/gcc/4.9/gcc/x86_64-apple-darwin15.4.0/4.9.3/include-fixed/math.h", line 276: error: expected an expression
#   return __inline_isfinited(__x) && __builtin_fabs(__x) >= __DBL_MIN__;
# To fix this comment below lines in above file:
#   #if 0
#       __header_always_inline int __inline_isnormald(double __x) {
#           return __inline_isfinited(__x) && __builtin_fabs(__x) >= __DBL_MIN__;
#       }
#   #endif
# Also there is an issue with parsing Random123 assembly intrinsics. For PDT parser we can use
# CRAY macro to remove use of assembly intrinsics. This should not impact performance much.
# -optPdtCOpts="-D_CRAYC=1". With this random123 for cray will be used which doesn't use any
# assembly intrinsics.
# llvm 4.0 has issues while compiling coreneuron due to avx 512 "undeclared dvi..." error
# llvm 8 from apple works fine on Sierra 10.12

#### LIST OF PACKAGES ####
_dev_packages=(
    'mod2c@develop'
    'mod2c@github'

    'nrnh5'

    'neuron@develop'
    'neuron@hdf'

    'reportinglib'

    'neurodamus@hdf'
    'neurodamus@develop'
    'neurodamus@master'

    'coreneuron@develop'
    'coreneuron@github'
    'coreneuron@hdf'
    'neuronperfmodels'
    'coreneuron@perfmodels'
)


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
# uninstall_package

# stop if iany package installation fails
set -e

export TAU_OPTIONS='-optPDTInst -optNoCompInst -optRevert -optPdtCOpts="-D_CRAYC=1" -optTauSelectFile=~/spackconfig/nrnperfmodels.tau'

# for every compiler, build each package
for compiler in "${compilers[@]}"
do
	for package in "${dev_packages[@]}"
    do
        spack install $package $compiler
    done
done
