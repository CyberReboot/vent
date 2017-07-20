OS=`uname -s`

build: clean
	@echo
	@echo "checking dependencies"
	@echo
	env
	docker version || true
	pip -V
	pip install -r tests/requirements.txt
	@for file in vent/core/*/; do mv $$file `echo $$file | tr '-' '_'` ; done 2> /dev/null || true
	rm -rf docs/source/v*.rst
	sphinx-apidoc -f -o docs/source/ vent/ \
 		vent/core/file-drop/test_file_drop.py \
 		vent/core/network-tap/ncontrol/test_ncontrol.py \
 		vent/core/rmq-es-connector/test_rmq_es_connector.py \
 		vent/core/rq-dashboard/rq_dash_settings.py \
 		vent/core/rq-dashboard/test_rq_dashboard.py \
 		vent/core/rq-worker/settings.py \
 		vent/core/rq-worker/test_rq_worker.py 
	make clean -C docs/
	make html -C docs/
	rm -rf docs/source/v*.rst
	@for file in vent/core/*/; do mv $$file `echo $$file | tr '_' '-'` ; done 2> /dev/null || true
	python setup.py install

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
	rm -rf docs/build/*
	rm -rf docs/source/v*.rst
	find . -name "*.pyc" -type f -delete
	find . -name "__pycache__" -delete
	pip uninstall -y vent || true

test: build
	py.test -s -v --cov=. -k 'not vendor' --cov-report term-missing

.PHONY: build test
