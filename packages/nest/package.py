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
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install nest
#
# You can edit this file again by typing:
#
#     spack edit nest
#
# See the Spack documentation for more information on packaging.
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
from spack import *
import string
import os

class Nest(Package):
    """FIXME: Put a proper description of your package here."""

    homepage = "https://github.com/nest/nest-simulator"
    github_url      = "https://github.com/nest/nest-simulator.git"

    version('develop', git=github_url, preferred=True)

    variant('mpi',           default=True,  description="Enable MPI support")
    variant('openmp',        default=True,  description="Enable OpenMP support")
    variant('python',        default=True,  description="Enable python bindings")
    variant('gsl',           default=True,  description="Enable GNU Scientific Library")
    variant('profile',       default=False, description="Enable profiling using Tau")
    variant('knl',           default=False, description="Enable KNL specific flags")
    variant('static',        default=False, description="Build static libraries")


    depends_on('mpi', when='+mpi')
    depends_on('gsl', when='+gsl')
    depends_on('python@2.6:', when='+python')
    depends_on('cmake@2.8.12:', type='build')
    depends_on('tau', when='+profile')
    depends_on('py-cython@0.19.2:', when='+python')

    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    def profiling_wrapper_off(self):
        if self.spec.satisfies('+profile'):
            del os.environ["USE_PROFILER_WRAPPER"]

    def get_optimization_level(self):
        flags = "-g"

        if 'bgq' in self.spec.architecture:
            flags += ' -O3'
        else:
            flags += ' -O2'

        if self.spec.satisfies('+knl'):
            flags = '-g -xmic-avx512 -O3 -qopt-report=5'

        return flags

    def install(self, spec, prefix):
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
                       '-Dwith-readline=OFF'
                       ]

            # not sure the -Dwith-optimize=flags option is required if we already set CMAKE_C_FLAGS above
            # but just to be safe
            semicolon_separated_optflag = optflag.translate(string.maketrans(' ',';'))
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

        # I wish there was a way to detect the specs here.
        # If the user didn't want python, no need to pollute their env.
        # How to get python version specified by user???
        if not self.spec.satisfies('~python'):
            py_version_string = 'python{0}'.format(self.spec['python'].version.up_to(2))
            nest_package_py_path = os.path.join(self.prefix.lib64, py_version_string, 'site-packages')
            print('PYTHONPATH')
            print(nest_package_py_path)
            run_env.prepend_path('PYTHONPATH', nest_package_py_path)








