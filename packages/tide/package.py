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
import os


class Tide(CMakePackage):

    """Tide is BlueBrain's Tiled Interactive Display Environment.
       It provides multi-window, multi-user touch interaction on large
       surfaces - think of a giant collaborative wall-mounted tablet."""

    homepage = "https://github.com/BlueBrain/Tide"
    url      = "https://github.com/BlueBrain/Tide.git"

    version('master', git=url, submodules=True, preferred=True)
    version('1.3.1', git=url, tag='1.3.1', submodules=True)
    version('1.3.0', git=url, tag='1.3.0', submodules=True)
    version('1.2.2', git=url, tag='1.2.2', submodules=True)

    depends_on('mpi')
    depends_on('zeroeq')
    depends_on('deflect')
    depends_on('qt@5.4:')
    depends_on('boost@1.54:')
    depends_on('libjpeg-turbo')
    depends_on('cmake@3:', type='build')

    def cmake_args(self):
        args = ['-DCLONE_SUBPROJECTS=ON']
        return args
