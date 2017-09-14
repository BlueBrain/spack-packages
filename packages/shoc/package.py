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
import llnl.util.tty as tty
from os import environ


class Shoc(AutotoolsPackage):
    """The Scalable HeterOgeneous Computing (SHOC) benchmark suite is a
       collection of benchmark programs testing the performance and
       stability of systems using computing devices with non-traditional
       architectures for general purpose computing."""

    homepage = "https://github.com/vetter/shoc"
    url = "https://github.com/vetter/shoc.git"

    # TODO: add new releases once available
    version('develop', git=url)

    variant('mpi',   default=True,  description='Build with MPI support')
    variant('cuda',  default=True,  description='Enable CUDA Support')

    depends_on('mpi', when='+mpi')
    depends_on('cuda', when='+cuda')

    @run_before('configure')
    def check_environment(self):
        # NOTO shoc benchmark expects user to set target architecture
        # for newer version of CUDA
        spec = self.spec
        if spec.satisfies('^cuda@7:') and environ.get('CUDA_CPPFLAGS') is None:
            msg = 'Make sure to set CUDA_CPPFLAGS environmental variable'
            msg += '(e.g."-gencode=arch=compute_20,code=sm_20")'
            tty.warn(msg)
