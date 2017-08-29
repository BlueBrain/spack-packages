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


class Reportinglib(CMakePackage):

    """Soma and full compartment report library developed at BBP"""

    homepage = "https://bbpcode.epfl.ch/code/a/sim/reportinglib/bbp"
    url      = "ssh://bbpcode.epfl.ch/sim/reportinglib/bbp"

    version('develop', git=url, preferred=True)

    # temporary version for branch being tested for INCITE
    version('gather', git=url, branch='sandbox/king/gatherMappingREP-31')

    variant('profile', default=False, description="Enable profiling using Tau")
    variant('static',  default=False, description="Build static library")

    depends_on('cmake@2.8.12:', type='build')
    depends_on('mpi')
    depends_on('tau', when='+profile')

    @run_before('install')
    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    @run_after ('install')
    def profiling_wrapper_off(self):
        if self.spec.satisfies('+profile'):
            del os.environ["USE_PROFILER_WRAPPER"]

    def cmake_args(self):

        spec   = self.spec

        # reportinglib tests are not running actual tests
        # and on osx we don't want to build boost from gcc
        options = ['-DUNIT_TESTS=OFF']

        if spec.satisfies('+profile'):
            env['CC']  = 'tau_cc'
            env['CXX'] = 'tau_cxx'
        # for bg-q, our cmake needs mpi compilers as c, cxx compiler
        elif 'bgq' in self.spec.architecture:
            env['CC']  = spec['mpi'].mpicc
            env['CXX'] = spec['mpi'].mpicxx

        # while building with tau, coreneuron needed static version
        if spec.satisfies('+static'):
            options.append('-DCOMPILE_LIBRARY_TYPE=STATIC')

        return options
