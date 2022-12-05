import json
from google.cloud import secretmanager


def get_secret(gcp_project_id, secret_name, secret_version):
    client = secretmanager.SecretManagerServiceClient()
    # For Local_DockerContainer Credential
    # with open('service_account.json', 'r') as f:
    #     credential = f.read()
    # service_account_info = json.loads(credential)
    # client = secretmanager.SecretManagerServiceClient.from_service_account_info(info=service_account_info)
    secret = client.secret_version_path(gcp_project_id, secret_name, secret_version)
    response = client.access_secret_version(name=secret)

    return response.payload.data.decode('UTF-8')
