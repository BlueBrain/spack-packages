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

    """
    HDF5 interface for neuron and coreneuron
    """

    homepage = "https://bbpteam.epfl.ch/reps/user/kumbhar/nrnh5/"
    url      = "ssh://bbpcode.epfl.ch/user/kumbhar/nrnh5"

    version('develop', git='ssh://bbpcode.epfl.ch/user/kumbhar/nrnh5')

    depends_on('cmake@2.8.12:', type='build')
    depends_on("mpi")
    depends_on("hdf5")

    def install(self, spec, prefix):

        with working_dir("spack-build", create=True):
            options = std_cmake_args
            options.extend([
                '-DBUILD_SHARED_LIBS=OFF'
                ])
            cmake('..', *options)
            make()
            make('install')

    #for convenience, set include path and library to link. this is
    #just for convenience purpose for neuron build which doesn't use
    #cmake to find package automatically
    def setup_dependent_package(self, module, dspec):

        libname = 'libnrnh5core.a'
        libdir = self.prefix.lib

        self.spec.include_path = '%s/nrnh5' %(self.spec.prefix.include)
        self.spec.library_path = libdir
        self.spec.link_library = "-lnrnh5core"
