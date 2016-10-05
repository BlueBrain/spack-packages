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
    version('master', git='ssh://bbpcode.epfl.ch/sim/coreneuron')

    variant('mpi', default=True, description="Enable MPI support")
    variant('openmp', default=True, description="Enable OpenMP support")
    variant('hdf5', default=True, description="Enable HDF5 data reading support")
    variant('neurodamus', default=True, description="Build mechanisms from Neurodamus")
    variant('report', default=True, description="Enable soma/compartment report with ReportingLib")
    variant('tests', default=False, description="Enable building tests")

    #mandatory dependencies
    depends_on('mod2c', type='build')
    depends_on('cmake@2.8.12:', type='build')
    depends_on("mpi")
    depends_on("nrnh5", when='+hdf5')
    depends_on('hdf5', when='+hdf5')
    depends_on('neurodamus', when='+neurodamus')

    #optional dependencies
    depends_on('neurodamus', when='+neurodamus', type='build')
    depends_on('reportinglib', when='+report')
    depends_on('boost', when='+tests')

    def install(self, spec, prefix):

        with working_dir("spack-build", create=True):

            options = [
                '-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
                '-DCOMPILE_LIBRARY_TYPE=STATIC',
                ]

            if spec.satisfies('+tests'):
                options.extend(['-DUNIT_TESTS:BOOL=ON', '-DFUNCTIONAL_TESTS:BOOL=ON'])
            else:
                options.extend(['-DUNIT_TESTS:BOOL=OFF', '-DFUNCTIONAL_TESTS:BOOL=OFF'])

            if spec.satisfies('+report'):
                options.extend(['-DENABLE_REPORTINGLIB:BOOL=ON'])

            if spec.satisfies('~hdf5'):
                options.extend(['-DENABLE_HDF5:BOOL=OFF'])

            if spec.satisfies('~mpi'):
                options.extend(['-DENABLE_MPI:BOOL=OFF'])

            if spec.satisfies('+neurodamus'):
                modlib_dir = '%s/lib/modlib' % (self.spec['neurodamus'].prefix)
                modfile_list = '%s/coreneuron_modlist.txt' % (modlib_dir)

                options.extend(['-DADDITIONAL_MECHPATH=%s' % (modlib_dir)])
                options.extend(['-DADDITIONAL_MECHS=%s' % (modfile_list)])

            #for bg-q, our cmake is not setup properly
            if spec.satisfies('+mpi') and str(spec.architecture) == 'bgq-CNK-ppc64':
                options.extend(['-DCMAKE_C_COMPILER=%s' % spec['mpi'].mpicc,
                                '-DCMAKE_CXX_COMPILER=%s' % spec['mpi'].mpicxx
                                ])

            cmake('..', *options)
            make()
            make('install')
