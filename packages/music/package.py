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
import shutil


class Music(AutotoolsPackage):
    """MUSIC, the MUltiSimulation Coordinator"""

    homepage = "https://github.com/INCF/MUSIC"
    url      = "https://github.com/INCF/MUSIC.git"

    #TODO: update release once available
    version('master', git=url)

    variant('mpi',    default=True, description='Enable MPI support')
    variant('python', default=True, description='Enable PyMUSIC')

    depends_on('mpi',       when='+mpi')
    depends_on('mpi',       when='+python')
    depends_on('py-mpi4py', when='+python')
    depends_on('py-cython', when='+python')

    depends_on('autoconf', type='build')
    depends_on('automake', type='build')
    depends_on('libtool', type='build')
    depends_on('m4', type='build')

    def configure_args(self):
        spec  = self.spec
        args  = ['--disable-anysource']
        flags = '-g -O2'

        if spec.satisfies('+mpi'):
            env['MPI_CXX'] = spec['mpi'].mpicxx
            args.append('--enable-mpi')
        else:
            args.append('--disable-mpi')

        if spec.satisfies('+python'):
            args.append('--with-python')
        else:
            args.append('--without-python')

        # NOTE: it is mandatory to set some mpi env variables even
        # for non-mpi build and must be non-empty string
        env['MPI_CFLAGS'] = flags
        env['MPI_CXXFLAGS'] = flags
        env['MPI_LDFLAGS'] = ' '

        return args
