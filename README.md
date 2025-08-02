# k8s_cluster_selection

This project helps you select and manage Kubernetes clusters.

## Requirements

- [Docker](https://docs.docker.com/get-docker/) installed on your system.
- [LM Studio](https://lmstudio.ai/) installed and running.
	- Download and run the "google/gemma-3-12b" model in LM Studio.

## Building the Container

1. Clone the repository:
	```bash
	git clone https://github.com/jeffbeagley/k8s_cluster_selection.git
	cd k8s_cluster_selection
	```

2. Build the Docker image:
	```bash
	docker build -t k8s_cluster_selection .
	```

## Running the Project

Use the provided `run.sh` script to start the application, replacing <user_input> with information about your cluster. Ie, "cluster a development"

```bash
./run.sh "<user_input>"
```

This will run the container and start the application.

## Notes

- Ensure Docker is running before executing the commands.
- Modify `run.sh` as needed for your environment.
- For more details, check the script and Dockerfile.