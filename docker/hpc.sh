set -e
set -x

#add compilers
spack compiler find

#mpich
spack install mpich

#install scorep
spack install cube +gui
spack install scorep@2.0.2 ^cube +gui

#install pdt + tau
spack install tau +download +scorep

#install extrae
spack install extrae

#install hpctoolkit
spack install hpctoolkit

#openspeedshop
spack install openspeedshop

#install stat
spack install stat
