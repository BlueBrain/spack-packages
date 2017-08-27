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


class Nest(Package):
    """NEST is a simulator for spiking neural network models that focuses
    on the dynamics, size and structure of neural systems rather than on
    the exact morphology of individual neurons. The development of NEST
    is coordinated by the NEST Initiative."""

    homepage = "http://www.nest-simulator.org/"
    url      = "https://github.com/nest/nest-simulator/archive/v2.12.0.tar.gz"
    giturl   = "https://github.com/nest/nest-simulator"
    alburl   = "https://github.com/alberto-antonietti/nest-simulator"

    version('2.12.0', '57e6f3f5fc888113dd07e896b695297b')
    version('2.10.0', 'e97371d8b802818c4a7de35276470c0c')
    version('2.8.0',  '3df9d39dfce8a85ee104c7c1d8e5b337')
    version('develop', git=giturl)
    version('alberto', git=alburl, branch='newtrasmitter')

    variant('mpi',      default=True,  description="Enable MPI support")
    variant('openmp',   default=True,  description="Enable OpenMP support")
    variant('python',   default=True,  description="Enable python bindings")
    variant('gsl',      default=True,  description="Enable GNU Scientific Library")
    variant('profile',  default=False, description="Enable profiling using Tau")
    variant('knl',      default=False, description="Enable KNL specific flags")
    variant('shared',   default=True,  description="Build shared libraries")
    variant('debug',    default=False,  description="Build type debug")

    depends_on('mpi', when='+mpi')
    depends_on('gsl', when='+gsl')
    depends_on('python@2.6:', when='+python')
    depends_on('cmake@2.8.12:', type='build')
    depends_on('tau', when='+profile')
    depends_on('py-cython@0.19.2:', when='+python')

    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    def get_optimization_level(self):
        flags = "-g -O2"

        if self.spec.satisfies('+knl') and self.spec.satisfies('%intel'):
            flags = '-xmic-avx512'
        return flags

    def patch(self):
        filter_file(r'EXACT', r'', 'cmake/ProcessOptions.cmake')
        filter_file(r'FATAL_ERROR "Your Cy', r'WARNING "Your Cy', 'cmake/ProcessOptions.cmake')
        filter_file(r'require_reg =.*$', r'return', 'extras/help_generator/helpers.py')

    def install(self, spec, prefix):
        build_dir = "spack-build-%s" % spec.version

        with working_dir(build_dir, create=True):
            c_compiler = spack_cc
            cxx_compiler = spack_cxx

            optflag = self.get_optimization_level()

            if spec.satisfies('+profile'):
                c_compiler = 'tau_cc'
                cxx_compiler = 'tau_cxx'
            # c, cxx compiler needs to be mpi wrapper on bg-q
            elif 'bgq' in spec.architecture and spec.satisfies('+mpi'):
                c_compiler = spec['mpi'].mpicc
                cxx_compiler = spec['mpi'].mpicxx

            cmake_options = ['-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
                             '-DCMAKE_C_COMPILER=%s' % c_compiler,
                             '-DCMAKE_CXX_COMPILER=%s' % cxx_compiler,
                             '-Dwith-ltdl=OFF',
                             '-Dwith-readline=OFF']


            if spec.satisfies('+debug'):
                cmake_options.extend(['-Dwith-optimize=OFF',
                                      '-DCMAKE_BUILD_TYPE=Debug'])
            else:
                semicolon_separated_optflag = optflag.translate(string.maketrans(' ', ';'))
                cmake_options.append('-Dwith-optimize=%s' % semicolon_separated_optflag)

            if 'bgq' in spec.architecture:
                cmake_options.append('-Denable-bluegene=Q')
                # sli exe link line needs qnostatic when +shared
                if spec.satisfies('+shared'):
                    cmake_options.append('-DCMAKE_EXE_LINKER_FLAGS=-qnostaticlink')

            if spec.satisfies('+python'):
                cmake_options.extend(['-Dwith-python=ON',
                                      '-Dcythonize-pynest=ON'])
            else:
                cmake_options.extend(['-Dwith-python=OFF',
                                      '-Dcythonize-pynest=OFF'])

            if spec.satisfies('+gsl'):
                cmake_options.append('-Dwith-gsl=%s' % spec['gsl'].prefix)
            else:
                cmake_options.append('-Dwith-gsl=OFF')

            if spec.satisfies('+mpi'):
                cmake_options.append('-Dwith-mpi=ON')
            else:
                cmake_options.append('-Dwith-mpi=OFF')

            if spec.satisfies('+openmp'):
                cmake_options.append('-Dwith-openmp=ON')
            else:
                cmake_options.append('-Dwith-openmp=OFF')

            if spec.satisfies('+shared'):
                cmake_options.append('-Dstatic-libraries=OFF')
            else:
                cmake_options.append('-Dstatic-libraries=ON')

            if spec.satisfies('%cce'):
                cmake_options.append('-Dwith-warning=OFF')

            cmake('..', *cmake_options)
            self.profiling_wrapper_on()
            make('VERBOSE=1')
            make('install')

    def setup_environment(self, spack_env, run_env):
        exe = '%s/nest' % self.prefix.bin
        run_env.set('NEST_EXE', exe)

        if self.spec.satisfies('+python'):
            eggs = find(self.prefix, 'PyNEST*egg*')
            if eggs:
                site_packages = os.path.dirname(find(self.prefix, 'PyNEST*egg*')[0])
                run_env.prepend_path('PYTHONPATH', site_packages)
