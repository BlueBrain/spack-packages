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

class Tuio(CMakePackage):

    """Tangible multitouch surfaces framework"""

    homepage = "https://github.com/BlueBrain/TUIO"
    url      = "https://github.com/BlueBrain/TUIO.git"

    version('develop', git=url, submodules=True)

    depends_on('cmake@3:', type='build')

    @run_before('cmake')
    def common_cxx11_abi_check(self):
        if self.spec.satisfies('%gcc@5:'):
            os.environ["CMAKE_COMMON_USE_CXX03_ABI"] = "1"
