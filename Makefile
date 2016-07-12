all: vent

all-no-cache: no-cache

latest: pull vent

test:
	@echo
	@echo "checking dependencies"
	@echo
	pip -V
 	pip install -r tests/requirements.txt
 	py.test -v --cov=. --cov-report term-missing

pull:
	docker pull boot2docker/boot2docker

vent: depends
	rm -rf images/*.tar
	docker build -t vent .
	docker run --rm vent > vent.iso
	rm -rf dependencies/tinycore-python2/python2.tar
	rm -rf management/vent-management.tar
.PHONY: vent

prebuilt: depends-prebuilt
	docker build -t vent .
	docker run --rm vent > vent.iso
	rm -rf dependencies/tinycore-python2/python2.tar
	rm -rf management/vent-management.tar

no-cache: depends-no-cache
	rm -rf images/*.tar
	docker build --no-cache -t vent .
	docker run --rm vent > vent.iso
	rm -rf dependencies/tinycore-python2/python2.tar
	rm -rf management/vent-management.tar

prebuilt-no-cache: depends-prebuilt-no-cache
	docker build --no-cache -t vent .
	docker run --rm vent > vent.iso
	rm -rf dependencies/tinycore-python2/python2.tar
	rm -rf management/vent-management.tar
	rm -rf images/*.tar

depends:
	@echo
	@echo "checking dependencies"
	@echo
	docker -v
	./build.sh

depends-no-cache:
	@echo
	@echo "checking dependencies"
	@echo
	docker -v
	./build.sh --no-cache

depends-prebuilt:
	@echo
	@echo "checking dependencies"
	@echo
	docker -v
	./build.sh --build-plugins

depends-prebuilt-no-cache:
	@echo
	@echo "checking dependencies"
	@echo
	docker -v
	./build.sh --build-plugins --no-cache

install:
	@echo
	@echo "installing vent and vent-generic to /usr/local/bin/"
	@echo "------"
	cp vent /usr/local/bin/vent
	cp vent /usr/local/bin/vent-generic
	@echo "------"
	@echo
.PHONY: install

images: depends-prebuilt
	@echo
	@echo "checking dependencies"
	@echo
	zip -v
	zip -r images images/
	@echo
	@echo "------"
	@echo "run this to inject the container images into the vent instance once it's been created:"
	@echo "unzip images.zip; cd images; vent <name_of_vent_machine> tar"
	@echo "------"
	@echo

clean:
	rm -rf images
	rm -rf images.zip
	rm -rf dependencies/tinycore-python2/python2.tar
	rm -rf management/vent-management.tar
	rm -vf vent.iso
.PHONY: clean
