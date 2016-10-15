set -e
set -x

#add compilers
spack compiler find

#mpich
spack install mpich

#install scorep
RUN spack install cube +gui
RUN spack install scorep@2.0.2 ^cube +gui

#install pdt + tau
RUN spack install tau +download +scorep

#install extrae
RUN spack install extrae

#install hpctoolkit
RUN spack install hpctoolkit

#openspeedshop
RUN spack install openspeedshop

#install stat
RUN spack install stat
