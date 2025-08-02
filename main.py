import lmstudio as lms
import os
import json
import subprocess
import sys

SERVER_API_HOST = os.getenv("LMSTUDIO_SERVER_HOST", "localhost:1234")
LOCAL_CLUSTER_CACHE_FILE = "clusters.json"

# Initialize LM Studio client
lms.configure_default_client(SERVER_API_HOST)

# Function to get AKS clusters from Azure
# This function checks for a local cache file first, and if it doesn't exist, it fetches the clusters using Azure CLI commands.
# The results are then cached for future use to avoid repeated API calls.
def get_clusters():
    # Check if cache file exists
    if os.path.exists(LOCAL_CLUSTER_CACHE_FILE):
        with open(LOCAL_CLUSTER_CACHE_FILE, "r") as f:
            return json.load(f)

    try:
        # Get all subscription IDs
        sub_cmd = 'az account list --query "[].id" -o tsv'
        sub_result = subprocess.run(sub_cmd, shell=True, capture_output=True, text=True)
        subscriptions = sub_result.stdout.strip().split("\n")

        # Initialize result list
        clusters = []

        # Iterate through subscriptions
        for sub_id in subscriptions:
            # Get AKS clusters for the subscription
            aks_cmd = f'az aks list --subscription {sub_id} --query "[].{{name:name, resourceGroup:resourceGroup, tags:tags}}" -o json'
            aks_result = subprocess.run(
                aks_cmd, shell=True, capture_output=True, text=True
            )

            if aks_result.stdout:
                aks_list = json.loads(aks_result.stdout)
                for cluster in aks_list:
                    clusters.append(
                        {
                            "cluster_name": cluster["name"],
                            "resource_group_name": cluster["resourceGroup"],
                            "subscription_id": sub_id,
                            "tags": cluster["tags"],
                        }
                    )

        # Cache the results
        with open(LOCAL_CLUSTER_CACHE_FILE, "w") as f:
            json.dump(clusters, f)

        return clusters
    except Exception as e:
        print(f"Error fetching clusters: {str(e)}")
        return []

# Function to log into a specific AKS cluster
# This function uses the Azure CLI to log into the specified AKS cluster using its subscription ID
# and resource group name. It returns a success message or an error message if the login fails
def login_to_cluster(subscription_id: str, resource_group_name: str, cluster_name: str):
    """Login to the specified AKS cluster using its subscription ID and resource group name."""
    try:
        # Login to the specified AKS cluster
        print(
            f"Logging into cluster: {cluster_name} in resource group: {resource_group_name} under subscription: {subscription_id}"
        )
        login_cmd = f"az aks get-credentials --subscription {subscription_id} --resource-group {resource_group_name} --name {cluster_name}"
        subprocess.run(login_cmd, shell=True, check=True)
        return f"Successfully logged into cluster: {cluster_name}"
    except subprocess.CalledProcessError as e:
        return f"Error logging into cluster: {str(e)}"

def get_cluster(text: str, clusters):
    try:
        model = lms.llm("google/gemma-3-12b")  # Use your loaded model
        chat = lms.Chat()

        chat.add_user_message(
            "You need to analyze the following text input, and choose the best object from the provided context"
        )
        chat.add_user_message(
            "Once you have the correct object, you will login to the cluster with the right values"
        )
        chat.add_user_message("Context: " + json.dumps(clusters, indent=2))
        chat.add_user_message(f"Text Input: {text}")

        response = model.act(chat, [login_to_cluster])

        return response
    except Exception as e:
        return f"LLM Error: {str(e)}"

if __name__ == "__main__":
    text_value = sys.argv[1]
    clusters = get_clusters()

    cluster = get_cluster(text_value, clusters)
