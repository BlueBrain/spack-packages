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

    version('1.3.1',   git=url, tag='1.3.1', submodules=True)
    version('1.3.0',   git=url, tag='1.3.0', submodules=True)
    version('develop', git=url, submodules=True, preferred=True)

    variant('touch',    default=True,  description="Enable TUIO touch listener")
    variant('movie',    default=True,  description="Enable FFMPEG movie support")
    variant('rest',     default=True,  description="Enable REST interface using ZeroEQ")
    variant('keyboard', default=True,  description="Enable virtual keyboard support")
    variant('knl',      default=False, description="Compile for KNL architecture")

    depends_on('mpi')
    depends_on('deflect')
    depends_on('qt@5.4:')
    depends_on('boost@1.54:')
    depends_on('libjpeg-turbo')

    depends_on('zeroeq', when='+rest')
    depends_on('tuio',   when='+touch')
    depends_on('ffmpeg', when='+movie')
    depends_on('virtualkeyboard', when='+keyboard')
    depends_on('cmake@3:', type='build')

    @run_before('cmake')
    def common_cxx11_abi_check(self):
        if self.spec.satisfies('%gcc@5:'):
            os.environ["CMAKE_COMMON_USE_CXX03_ABI"] = "1"

    def get_knl_flag(self, spec):
        flags = ""
        if spec.satisfies('%gcc'):
            flags = "-march=knl -mavx512f -mavx512pf -mavx512er -mavx512cd"
        elif spec.satisfies('%intel'):
            flags = "-xMIC-AVX512"
        elif spec.satisfies('%clang'):
            flags = "-march=knl"
        return flags

    def cmake_args(self):
        spec = self.spec
        args = ['-DDISABLE_SUBPROJECTS=ON']
        args.extend(['-DTIDE_ENABLE_MOVIE_SUPPORT=%s'       % ('ON' if '+movie' in spec else 'OFF'),
                     '-DTIDE_ENABLE_REST_INTERFACE=%s'      % ('ON' if '+rest' in spec else 'OFF'),
                     '-DTIDE_ENABLE_TUIO_TOUCH_LISTENER=%s' % ('ON' if '+touch' in spec else 'OFF')])
        if '+knl' in spec:
            flags = get_knl_flag()
            args.append('-DCMAKE_C_FLAGS=%s' % flags)
            args.append('-DCMAKE_CXX_FLAGS=%s' % flags)

        return args

    def setup_environment(self, spack_env, run_env):
        spec = self.spec
        run_env.set('IPATH_NO_CPUAFFINITY', 1)
        if not spec.satisfies('^openmpi'):
            run_env.set('MV2_ENABLE_AFFINITY', 0)
