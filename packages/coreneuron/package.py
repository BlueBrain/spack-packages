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


class Coreneuron(Package):

    """
    CoreNEURON is a simplified engine for the NEURON simulator optimised for both
    memory usage and computational speed. Its goal is to simulate massive cell
    networks with minimal memory footprint and optimal performance.
    """

    homepage = "https://github.com/BlueBrain/CoreNeuron"
    url      = "ssh://bbpcode.epfl.ch/sim/coreneuron"

    version('develop', git='ssh://bbpcode.epfl.ch/sim/coreneuron', branch='sandbox/kumbhar/nrnh5')

    variant('openmp', default=True, description="Enable OpenMP support")
    variant('hdf5', default=False, description="Enable HDF5 data reading support")
    variant('neurodamus', default=False, description="Build mechanisms from Neurodamus")
    variant('report', default=False, description="Enable soma/compartment report with ReportingLib")
    variant('tests', default=False, description="Enable building tests")

    #mandatory dependencies
    depends_on('mod2c', type='build')
    depends_on('cmake@2.8.12:', type='build')
    depends_on("mpi")
    depends_on("nrnh5", when='+hdf5')

    #optional dependencies
    depends_on('hdf5', when='+hdf5')
    depends_on('neurodamus', when='+neurodamus', type='build')
    depends_on('reportinglib', when='+report')
    depends_on('boost', when='+tests')

    def install(self, spec, prefix):

        with working_dir("spack-build", create=True):
            options = std_cmake_args
            #options.extend([
            #    '-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
            #    '-DCOMPILE_LIBRARY_TYPE=STATIC',
            #    ])

            if '+tests' in spec:
                options.extend(['-DUNIT_TESTS:BOOL=ON', '-DFUNCTIONAL_TESTS:BOOL=ON'])
            else:
                options.extend(['-DUNIT_TESTS:BOOL=OFF', '-DFUNCTIONAL_TESTS:BOOL=OFF'])

            if '+report' in spec:
                options.extend(['-DENABLE_REPORTINGLIB:BOOL=ON'])

            if '+hdf5' not in spec:
                options.extend(['-DENABLE_HDF5:BOOL=OFF'])

            cmake('..', *options)
            make()
            make('install')
