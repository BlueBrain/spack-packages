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
    variant('zlib', default=False, description="Link with Zlib")

    depends_on('cmake@2.8.12:', type='build')
    depends_on("mpi")
    depends_on("hdf5")
    depends_on("zlib", when='+zlib')

    def get_arch_build_options(self):
        return []

    @when('arch=bgq-CNK-ppc64')
    def get_arch_build_options(self, spec):
        return ['-DCMAKE_C_COMPILER=%s' % spec['mpi'].mpicc,
                '-DCMAKE_CXX_COMPILER=%s' % spec['mpi'].mpicxx,
                '-DENABLE_MPI_LIB_LINK:BOOL=OFF']

    def install(self, spec, prefix):

        with working_dir("spack-build", create=True):
            options = ['-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
                       '-DBUILD_SHARED_LIBS=OFF']

            options.extend(self.get_arch_build_options(spec))

            if spec.satisfies('+zlib'):
                options.extend(['-DZLIB_ROOT=%s' % spec['zlib'].prefix,
                                '-DENABLE_ZLIB_LINK:BOOL=ON'])

            cmake('..', *options)
            make()
            make('install')

    # for convenience, set include path and library to link. this is
    # just for convenience purpose for neuron build which doesn't use
    # cmake to find package automatically
    def setup_dependent_package(self, module, dspec):
        self.spec.include_path = '%s/nrnh5' % (self.spec.prefix.include)
        self.spec.link_library = "-lnrnh5core"
