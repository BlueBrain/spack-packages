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


class Learningengine(CMakePackage):
    """Testing framework for LE"""

    homepage = "ssh://bbpcode.epfl.ch/hpc/learning_engine"
    url      = "ssh://bbpcode.epfl.ch/hpc/learning_engine"

    version('develop', git=url)

    variant('tests',        default=True,  description="Build the regression tests")
    variant('benchmark',    default=True, description="Enable benchmarks")
    variant('pybinding',    default=True, description="Enable Python Binding")
    variant('cuda',         default=False, description="Enable CUDA")
    variant('docs',         default=False, description="Enable Python Docs")
    variant('syn2',         default=False, description="Enable Syn2 reader")
    variant('knl',          default=False, description="Build for KNL")

    variant('threading',    default='tbb', values=('tbb', 'omp', 'seq'),
            multi=False, description="Threading backends"
    )

    variant('random',       default='standard', values=('mkl', 'standard'),
            multi=False, description="Random number generators"
    )

    variant('precision',    default='double', values=('double', 'float'),
            multi=False, description="Floating Point Precision"
    )

    depends_on('python@2.7:',         when='+pybinding')
    depends_on('py-cython',           when='+pybinding')
    depends_on("intel-tbb",           when='threading=tbb')
    depends_on("cuda",                when='+cuda')
    depends_on("boost@1.52:")
    depends_on('syntool',             when='+syn2')
    depends_on('highfive@master~mpi', when='+syn2')
    depends_on('py-sphinx',           when='+docs')

    conflicts('%gcc', when='random=mkl')
    conflicts('%clang', when='random=mkl')

    def get_optimization_flags(self):
        flags = "-g -O2"
        if self.spec.satisfies('%intel'):
            flags += ' -qopt-report=5'
        if self.spec.satisfies('+knl'):
            flags = ' -xmic-avx512'

        return flags

    def cmake_args(self):
        spec = self.spec
        optflag = self.get_optimization_flags()

        args = ['-DCMAKE_C_FLAGS=%s' % optflag,
                '-DCMAKE_CXX_FLAGS=%s' % optflag]

        if spec.satisfies('+tests'):
            args.append('-DLEARNING_ENGINE_TESTS=ON')
        else:
            args.append('-DLEARNING_ENGINE_TESTS=OFF')

        if spec.satisfies('+cuda'):
            args.append('-DLEARNING_ENGINE_CUDA=ON')
        else:
            args.append('-DLEARNING_ENGINE_CUDA=OFF')

        if spec.satisfies('+benchmark'):
            args.append('-DLEARNING_ENGINE_BENCHMARK=ON')
        else:
            args.append('-DLEARNING_ENGINE_BENCHMARK=OFF')

        if spec.satisfies('+pybinding'):
            args.append('-DLEARNING_ENGINE_PYTHON_BINDING=ON')
        else:
            args.append('-DLEARNING_ENGINE_PYTHON_BINDING=OFF')

        if spec.satisfies('+docs'):
            args.append('-DLEARNING_ENGINE_SPHINX=ON')
        else:
            args.append('-DLEARNING_ENGINE_SPHINX=OFF')

        if spec.satisfies('+syn2'):
            args.append('-DLEARNING_ENGINE_SYN2=ON')
        else:
            args.append('-DLEARNING_ENGINE_SYN2=OFF')

        args.append('-DOPT_THREAD=%s' % spec.variants['threading'].value)
        args.append('-DOPT_RANDOM=%s' % spec.variants['random'].value)
        args.append('-DOPT_PRECISION=%s' % spec.variants['precision'].value)

        return args
