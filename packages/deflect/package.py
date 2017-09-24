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

class Deflect(CMakePackage):

    """C++ library for building applications to stream pixels to Tide"""

    homepage = "https://github.com/BlueBrain/Deflect"
    url      = "https://github.com/BlueBrain/Deflect.git"

    version('0.13.0',  git=url, tag='0.13.0',     submodules=True)
    version('0.12.1',  git=url, tag='0.12.1',     submodules=True)
    version('develop', git=url, submodules=True)

    depends_on('qt@5.4:')
    depends_on('boost@1.54:')
    depends_on('libjpeg-turbo')
    depends_on('cmake@3:', type='build')

    @run_before('cmake')
    def common_cxx11_abi_check(self):
        if self.spec.satisfies('%gcc@5:'):
            os.environ["CMAKE_COMMON_USE_CXX03_ABI"] = "1"
