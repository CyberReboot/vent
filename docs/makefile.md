### `Makefile` targets

There main target builds the vent ISO without any of the containers that will need to be built after the fact. This allows the ISO to be a mere 40MB.  If you use one of the `prebuilt` options it will also build all of the necessary containers and tarball them up.  You can then use the `vent` utility after the vent instance is created inside the local `images` directory specifying `tar` as an argument, and it will add the tarballs as docker images on the instance.

#### `make all`

This target (the default target if none is supplied) will build the ISO.

#### `make all-no-cache`

This will build the ISO, but it won't use cache.

#### `make vent`

This target will build the minimal image without building the containers and build/extract the ISO from the final result.

#### `make prebuilt`

This target will build the minimal image as well as tarballs of all of the images after building all the containers and build/extract the ISO from the final result.

#### `make no-cache`

This will build the same target, but it won't use cache.

#### `make prebuilt-no-cache`

This will build the same target and the tarballs, but it won't use cache.

#### `make images`

This will build the containers and export them as tarballs into the images directory and then make a zip of those tarballs.

#### `make install`

This will install `vent` and `vent-generic` into the path and can be used for loading in tarball images or copying up PCAPs or other files to a vent instance.

#### `make clean`

This will remove all of the tarballs and ISOs created from any of the build processes.
