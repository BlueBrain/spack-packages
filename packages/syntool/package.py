##############################################################################
# Copyright (c) 2013-2017, Lawrence Livermore National Security, LLC.
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
#     spack install synapse-tool
#
# You can edit this file again by typing:
#
#     spack edit synapse-tool
#
# See the Spack documentation for more information on packaging.
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
from spack import *


class Syntool(CMakePackage):
    """SYN-TOOL provides a C++ and a python API to read / write neuron
       connectivity informations. SYN-TOOL is designed to support large
       connecitivy data with Billions of connections."""

    homepage = "https://bbpcode.epfl.ch/browse/code/hpc/synapse-tool"
    url      = "ssh://bbpcode.epfl.ch/hpc/synapse-tool"

    version('master', git=url, submodules=True)
    variant('mpi', default=True, description="Enable MPI backend")

    depends_on('hdf5')
    depends_on('boost@1.55:')
    depends_on('python')
    depends_on('mpi', when='+mpi')
    depends_on('cmake@2.8:', type='build')

    def cmake_args(self):
        args = []
        spec = self.spec

        if spec.satisfies('+mpi'):
            args.append('-DSYNTOOL_WITH_MPI=ON')
            env['CC']  = spec['mpi'].mpicc
            env['CXX'] = spec['mpi'].mpicxx

        return args
