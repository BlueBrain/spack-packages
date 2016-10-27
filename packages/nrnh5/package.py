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


class Nrnh5(Package):

    """HDF5 interface for neuron and coreneuron"""

    homepage = "https://bbpteam.epfl.ch/reps/user/kumbhar/nrnh5/"
    url      = "ssh://bbpcode.epfl.ch/user/kumbhar/nrnh5"

    version('develop', git='ssh://bbpcode.epfl.ch/user/kumbhar/nrnh5')

    depends_on('cmake@2.8.12:', type='build')
    depends_on('mpi')
    depends_on('hdf5')
    depends_on('zlib')

    def get_arch_build_options(self, spec):
        options = []

        if 'bgq' in self.spec.architecture:
            options.extend(['-DCMAKE_C_COMPILER=%s' % spec['mpi'].mpicc,
                            '-DCMAKE_CXX_COMPILER=%s' % spec['mpi'].mpicxx,
                            '-DENABLE_MPI_LIB_LINK:BOOL=OFF'])

        # intel15 doesn't compile gtest
        if 'cray' in self.spec.architecture:
            options.extend(['-DBUILD_TESTS:OFF=OFF'])

        return options

    def install(self, spec, prefix):

        with working_dir("spack-build", create=True):
            options = ['-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
                       '-DBUILD_SHARED_LIBS=OFF']

            options.extend(self.get_arch_build_options(spec))

            options.extend(['-DZLIB_ROOT=%s' % spec['zlib'].prefix,
                            '-DENABLE_ZLIB_LINK:BOOL=ON'])

            cmake('..', *options)
            make()
            make('install')

    # As NEURON is using autotools, set include paths and library to link.
    def setup_dependent_package(self, module, dspec):

        inc_path = '-I%s/nrnh5 -I%s' % (self.spec.prefix.include, self.spec['hdf5'].prefix.include)
        link_lib = '-L%s -lnrnh5core -L%s -lhdf5 -L%s -lz' % (
                    self.spec.prefix.lib, self.spec['hdf5'].prefix.lib,
                    self.spec['zlib'].prefix.lib)

        self.spec.include_path =  inc_path
        self.spec.link_library = link_lib
