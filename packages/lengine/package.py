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
    variant('profile',      default=False, description="Build with TAU")
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
    depends_on('tau', when='+profile')

    def get_optimization_flags(self):
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

            optflag = self.get_optimization_flags()

            if self.spec.satisfies('+profile'):
                c_compiler = 'tau_cc'
                cxx_compiler = 'tau_cxx'
            # for bg-q : c, cxx wrappers should be mpi wrappers
            if 'bgq' in self.spec.architecture and self.spec.satisfies('+mpi'):
                    c_compiler = self.spec['mpi'].mpicc
                    cxx_compiler = self.spec['mpi'].mpicxx

            cmake_options = ['-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
                             '-DCMAKE_C_FLAGS=%s' % optflag,
                             '-DCMAKE_CXX_FLAGS=%s' % optflag,
                             '-DCMAKE_C_COMPILER=%s' % c_compiler,
                             '-DCMAKE_CXX_COMPILER=%s' % cxx_compiler]
