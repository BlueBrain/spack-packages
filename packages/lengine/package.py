##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
import string
import os
from spack import *


class Lengine(Package):
    """Testing framework for LE"""

    homepage = "ssh://bbpcode.epfl.ch/hpc/learning_engine"
    url      = "ssh://bbpcode.epfl.ch/hpc/learning_engine"

    version('develop', git=url)

    variant('sandbox',      default=True,  description="Build the main (sandbox)")
    variant('draft',        default=True,  description="Build first draft")
    variant('tests',        default=True,  description="Build the regression tests")
    variant('cuda',         default=False, description="Enable CUDA")
    variant('mpi',          default=True, description="Enable MPI")
    variant('graph',        default=True, description="Enable boost graph")
    variant('benchmark',    default=True, description="Enable benchmarks")
    variant('gsl',          default=True,  description="Enable GSL")
    variant('pybinding',    default=True, description="Enable Python Binding")
    variant('slurm',        default=False, description="Enable Slurm")
    variant('docs',         default=False, description="Enable Python Docs")
    variant('syn2',         default=False, description="Enable Syn2 reader")
    variant('knl',          default=False, description="Build for KNL")
    variant('threading',    default='tbb', values=('tbb', 'omp', 'seq'),
            multi=False, description="Threading backends"
    )
    variant('random',       default='mkl', values=('mkl', 'standard'),
            multi=False, description="Random number generators"
    )

    depends_on('mpi', when='+mpi')
    depends_on('gsl', when='+gsl')
    depends_on('gsl', when='+draft')
    depends_on('cmake@3.1:', type='build')
    depends_on('python@2.7:', when='+pybinding')
    depends_on('py-cython', when='+pybinding')
    depends_on("tbb", when='threading=tbb')
    depends_on("slurm", type='build', when='+slurm')
    depends_on("cuda", when='+cuda')
    depends_on("boost@1.52:+graph+test+system+program_options")
    depends_on('syn2', when='+syn2')
    depends_on('highfive', when='+syn2')
    depends_on('py-sphinx', when='+docs')

    def get_optimization_level(self):
        flags = "-g -O2"

        if self.spec.satisfies('%intel'):
            flags += ' -qopt-report=5'

        if self.spec.satisfies('+knl'):
            flags = ' -xmic-avx512'

        return flags

    def install(self, spec, prefix):
        return

        build_dir = "spack-build-%s" % spec.version

        with working_dir(build_dir, create=True):
            c_compiler = spack_cc
            cxx_compiler = spack_cxx

            optflag = self.get_optimization_level()

            if self.spec.satisfies('+profile'):
                c_compiler = 'tau_cc'
                cxx_compiler = 'tau_cxx'
            # for bg-q, our cmake is not setup properly
            elif 'bgq' in self.spec.architecture and self.spec.satisfies('+mpi'):
                    c_compiler = self.spec['mpi'].mpicc
                    cxx_compiler = self.spec['mpi'].mpicxx

            cmake_options = ['-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
                             '-DCMAKE_C_FLAGS=%s' % optflag,
                             '-DCMAKE_CXX_FLAGS=%s' % optflag,
                             '-DCMAKE_C_COMPILER=%s' % c_compiler,
                             '-DCMAKE_CXX_COMPILER=%s' % cxx_compiler,
                             '-Dwith-ltdl=OFF',
                             '-Dwith-readline=OFF']

            # not sure the -Dwith-optimize=flags option is required if we already set CMAKE_C_FLAGS above
            # but just to be safe
            semicolon_separated_optflag = optflag.translate(string.maketrans(' ', ';'))
            cmake_options.extend(['-Dwith-optimize=' + semicolon_separated_optflag])

            if self.spec.satisfies('~python'):
                cmake_options.extend(['-Dwith-python=OFF'])
                cmake_options.extend(['-Dcythonize-pynest=OFF'])
            else:
                cmake_options.extend(['-Dwith-python=ON'])
                cmake_options.extend(['-Dcythonize-pynest=ON'])

            if self.spec.satisfies('~gsl'):
                cmake_options.extend(['-Dwith-gsl=OFF'])
            else:
                cmake_options.extend(['-Dwith-gsl=ON'])

            if self.spec.satisfies('~mpi'):
                cmake_options.extend(['-Dwith-mpi=OFF'])
            else:
                cmake_options.extend(['-Dwith-mpi=ON'])

            if self.spec.satisfies('~openmp'):
                cmake_options.extend(['-Dwith-openmp=OFF'])
            else:
                cmake_options.extend(['-Dwith-openmp=ON'])

            if self.spec.satisfies('~static'):
                cmake_options.extend(['-Dstatic-libraries=OFF'])
            else:
                cmake_options.extend(['-Dstatic-libraries=ON'])

            cmake('..', *cmake_options)
            self.profiling_wrapper_on()
            make()
            make('install')
            self.profiling_wrapper_off()

    def setup_environment(self, spack_env, run_env):
        exe = '%s/nest' % self.prefix.bin
        run_env.set('NEST_EXE', exe)

        # for mvapich2 module we need to setup MV2_ENABLE_AFFINITY
        # env variable to turn on multi-threading support
        run_env.set('MV2_ENABLE_AFFINITY', '0')

        # How to get python version specified by user???
        if self.spec.satisfies('+python'):
            py_version_string = 'python{0}'.format(self.spec['python'].version.up_to(2))
            nest_package_py_path = os.path.join(self.prefix.lib64, py_version_string, 'site-packages')
            run_env.prepend_path('PYTHONPATH', nest_package_py_path)
