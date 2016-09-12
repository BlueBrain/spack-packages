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


class Reportinglib(Package):

    """
    Soma and full compartment report library developed at BBP
    """

    homepage = "https://bbpcode.epfl.ch/code/a/sim/reportinglib/bbp"
    url      = "ssh://bbpcode.epfl.ch/sim/reportinglib/bbp"

    version('master', git='ssh://bbpcode.epfl.ch/sim/reportinglib/bbp')

    depends_on('cmake@2.8.12:', type='build')
    depends_on("mpi")

    def install(self, spec, prefix):

        with working_dir("spack-build", create=True):
            options = []
            options.extend([
                '-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
                '-DCOMPILE_LIBRARY_TYPE=STATIC',
                ])

            cmake('..', *options)
            make()
            make('install')
