OS=`uname -s`
PIP=$(shell which pip3 || echo "pip3")

build: clean
	@echo
	@echo "checking dependencies"
	@echo
	env
	docker version || true
	$(PIP) -V
	$(PIP) install -r requirements.txt
	$(MAKE) docs
	python3 setup.py install

docs: docs_clean
	@echo "generating documentation"
	sphinx-apidoc -f -o docs/source/ vent/ \
		vent/core/file_drop/test_file_drop.py \
 		vent/core/network_tap/ncontrol/test_ncontrol.py \
 		vent/core/rmq_es-_connector/test_rmq_es_connector.py \
 		vent/core/rq_dashboard/rq_dash_settings.py \
 		vent/core/rq_dashboard/test_rq_dashboard.py \
 		vent/core/rq_worker/settings.py \
 		vent/core/rq_worker/test_rq_worker.py

docs_clean:
	@echo "deleting all vent rst files"
	rm -rf docs/source/v*.rst

gpu: build
	@if hash nvidia-docker 2>/dev/null; then \
		echo "nvidia-docker found"; \
		docker pull nvidia/cuda:8.0-runtime; \
		if [ "${OS}" = "Linux" ] ; then \
			if [ -f /etc/redhat-release ] ; then \
				sudo sed -i '/ExecStart=\/usr\/bin\/nvidia-docker-plugin -s $$SOCK_DIR/c\ExecStart=\/usr\/bin\/nvidia-docker-plugin -s $$SOCK_DIR -l :3476' /usr/lib/systemd/system/nvidia-docker.service; \
				sudo systemctl daemon-reload; \
				sudo systemctl start nvidia-docker; \
			elif [ -f /etc/debian_version ] ; then \
				sudo sed -i '/ExecStart=\/usr\/bin\/nvidia-docker-plugin -s $$SOCK_DIR/c\ExecStart=\/usr\/bin\/nvidia-docker-plugin -s $$SOCK_DIR -l :3476' /lib/systemd/system/nvidia-docker.service; \
				sudo systemctl daemon-reload; \
				sudo systemctl restart nvidia-docker; \
			fi \
		fi \
	else \
		if [ "${OS}" = "Linux" ] ; then \
			docker pull nvidia/cuda:8.0-runtime; \
			if [ -f /etc/redhat-release ] ; then \
				wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker-1.0.1-1.x86_64.rpm && \
				sudo rpm -i /tmp/nvidia-docker*.rpm && rm /tmp/nvidia-docker*.rpm; \
				sudo sed -i '/ExecStart=\/usr\/bin\/nvidia-docker-plugin -s $$SOCK_DIR/c\ExecStart=\/usr\/bin\/nvidia-docker-plugin -s $$SOCK_DIR -l :3476' /usr/lib/systemd/system/nvidia-docker.service; \
				sudo systemctl daemon-reload; \
				sudo systemctl start nvidia-docker; \
			elif [ -f /etc/debian_version ] ; then \
				wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1-1_amd64.deb && \
				sudo dpkg -i /tmp/nvidia-docker*.deb && rm /tmp/nvidia-docker*.deb; \
				sudo sed -i '/ExecStart=\/usr\/bin\/nvidia-docker-plugin -s $$SOCK_DIR/c\ExecStart=\/usr\/bin\/nvidia-docker-plugin -s $$SOCK_DIR -l :3476' /lib/systemd/system/nvidia-docker.service; \
				sudo systemctl daemon-reload; \
				sudo systemctl restart nvidia-docker; \
			else \
				wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1_amd64.tar.xz && \
				sudo tar --strip-components=1 -C /usr/bin -xvf /tmp/nvidia-docker*.tar.xz && rm /tmp/nvidia-docker*.tar.xz && \
				sudo -b nohup nvidia-docker-plugin > /tmp/nvidia-docker.log; \
				echo "!!! Nvidia-docker-plugin needs to be configured to bind to all interfaces !!!"; \
			fi \
		else \
			echo "unable to install nvidia-docker on this host"; \
		fi \
	fi

clean:
	rm -rf .cache
	rm -rf .coverage
	rm -rf .vent
	rm -rf vent.egg-info
	rm -rf vent.iso
	rm -rf dist
	rm -rf build
	rm -rf plugins
	rm -rf core
	find . -name "*.pyc" -type f -delete
	find . -name "__pycache__" -delete
	$(PIP) uninstall -y vent || true

test: build
	pytest -l -s -v --cov=. --cov-report term-missing

test-menu: build
	pytest tests/menu/ -l -s -v --cov=. --cov-report term-missing

test-unit: build
	pytest tests/unit/ -l -s -v --cov=. --cov-report term-missing

test-plugins: build
	sudo service rabbitmq-server start &
	pytest vent/ -l -s -v --cov=. --cov-report term-missing
	sudo service rabbitmq-server stop

test-local: test-local-clean clean
	docker build -t vent-test -f Dockerfile.test .
	docker run -d --name vent-test-redis redis:alpine
	docker run -d --name vent-test-rabbitmq rabbitmq:3-management
	docker run -d --name vent-test-elasticsearch elasticsearch:2-alpine
	docker run -it -v /var/run/docker.sock:/var/run/docker.sock:rw --link vent-test-redis:redis --link vent-test-rabbitmq:localhost --link vent-test-elasticsearch:localhost vent-test

test-local-clean:
	docker rm -f vent-test-redis || true
	docker rm -f vent-test-rabbitmq || true
	docker rm -f vent-test-elasticsearch || true

.PHONY: build test
