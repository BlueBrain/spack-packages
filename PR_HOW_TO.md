[![Build Status](https://travis-ci.org/pramodskumbhar/spack-packages.svg?branch=master)](https://travis-ci.org/pramodskumbhar/spack-packages)

Repository of Spack packages for NEURON and Neuroscience related simulator development.


## Travis Configuration : Howto?

If you add new package or change existing package then make sure to update:

- If your package has other dependencies that can be installed via `apt-get` or `brew` then update :

    ```bash
    .travis/install_dependencies.sh
    ```

- Make sure to update the `packages.yaml` for `linux` or `osx` platform :

    ```bash
    packages.linux.yaml
    packages.osx.yaml
    ```

- Now if you want to test your new package then add spec to :

    ```bash
    install_packages.sh
    ```

    If your package can't be build on platform like OS X then add `spec` entry in relevant platform only :

    ```bash
    if [[ "$TRAVIS_OS_NAME" == "linux" ]]; then
        packages=(
        'mod2c'
        'coreneuron ~neurodamusmod ~report'
        'neuron'
        )

        # for module support on linux
        source /etc/profile.d/modules.sh
    else
        packages=(
        'mod2c'
        'coreneuron ~neurodamusmod ~report'
        'neuron'
        )

        # for module support on osx
        source /usr/local/opt/modules/Modules/init/bash;
    fi

    ```
