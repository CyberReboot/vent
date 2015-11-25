all: vent-minimal.iso # vent-prebuilt.iso

all-no-cache: vent-minimal-no-cache.iso # vent-prebuilt-no-cache.iso

vent-minimal.iso: depends-minimal
	docker build -t vent:minimal .
	docker run --rm vent:minimal > vent-minimal.iso
	rm -rf dependencies/tinycore-python2/python2.tar
	rm -rf management/vent-management.tar

vent-prebuilt.iso: depends-prebuilt
	docker build -t vent:prebuilt .
	docker run --rm vent:prebuilt > vent-prebuilt.iso
	rm -rf images
	rm -rf dependencies/tinycore-python2/python2.tar
	rm -rf management/vent-management.tar

vent-minimal-no-cache.iso: depends-minimal-no-cache
	docker build --no-cache -t vent:minimal .
	docker run --rm vent:minimal > vent-minimal.iso
	rm -rf dependencies/tinycore-python2/python2.tar
	rm -rf management/vent-management.tar

vent-prebuilt-no-cache.iso: depends-prebuilt-no-cache
	docker build --no-cache -t vent:prebuilt .
	docker run --rm vent:prebuilt > vent-prebuilt.iso
	rm -rf images
	rm -rf dependencies/tinycore-python2/python2.tar
	rm -rf management/vent-management.tar

depends-minimal:
	./build.sh

depends-minimal-no-cache:
	./build.sh --no-cache

depends-prebuilt:
	./build.sh --build-plugins

depends-prebuilt-no-cache:
	./build.sh --build-plugins --no-cache

clean:
	rm -rf images
	rm -rf dependencies/tinycore-python2/python2.tar
	rm -rf management/vent-management.tar
	rm -vf vent-*.iso
.PHONY: clean
