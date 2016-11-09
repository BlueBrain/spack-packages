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


class Reportinglib(Package):

    """Soma and full compartment report library developed at BBP"""

    homepage = "https://bbpcode.epfl.ch/code/a/sim/reportinglib/bbp"
    url      = "ssh://bbpcode.epfl.ch/sim/reportinglib/bbp"

    version('develop', git='ssh://bbpcode.epfl.ch/sim/reportinglib/bbp')

    variant('profile', default=False, description="Enable profiling using Tau")
    variant('static', default=False, description="Build static library")

    depends_on('cmake@2.8.12:', type='build')
    depends_on('mpi')
    depends_on('tau', when='+profile')

    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    def install(self, spec, prefix):

        build_dir = "spack-build-%s" % spec.version

        with working_dir(build_dir, create=True):

            options = ['-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix]

            c_compiler = spec['mpi'].mpicc
            cxx_compiler = spec['mpi'].mpicxx

            if spec.satisfies('+profile'):
                c_compiler = 'tau_cc'
                cxx_compiler = 'tau_cxx'
                # on darwin, boost is not always linked from gcc
                options.extend(['-DUNIT_TESTS=OFF'])

            # while building with tau, coreneuron needed static version
            if spec.satisfies('+static'):
                options.extend(['-DCOMPILE_LIBRARY_TYPE=STATIC'])

            # especially for bg-q
            options.extend(['-DCMAKE_C_COMPILER=%s' % c_compiler,
                            '-DCMAKE_CXX_COMPILER=%s' % cxx_compiler])

            cmake('..', *options)
            self.profiling_wrapper_on()
            make()
            make('install')
