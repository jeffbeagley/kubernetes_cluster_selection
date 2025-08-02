#/bin/bash

TEXT_VALUE="$1"  # Capture the text value from the script's command-line argument

docker run --rm \
	-v $(pwd):/app \
	-v /home/$(whoami)/.azure:/root/.azure \
	--network host -e LMSTUDIO_SERVER_HOST=192.168.1.41:1234 k8s-tool python /app/main.py "$TEXT_VALUE"