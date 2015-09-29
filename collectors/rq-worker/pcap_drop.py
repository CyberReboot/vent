def pcap_queue(path):
    # !! TODO read params for create_container from the templates!
    from docker import Client
    c = Client(base_url='unix://var/run/docker.sock')
    # !! TODO check modes for which plugins to enable
    # !! TODO for plugin, create container and start it
    container = c.create_container(image='ip/tshark', volumes=["/pcaps"], environment=["PYTHONUNBUFFERED=0"], tty=True, stdin_open=True, command=path)
    response = c.start(container=container.get('Id'), binds=["/pcaps:/pcaps:ro"], links={"collectors-rabbitmq":"rabbitmq"})
    return response
