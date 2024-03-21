import paramiko
from io import StringIO
import os
from google.auth import default
from google.cloud import storage


def get_cloudbuild_private_key(blob="creds/ssh-private-key-cloudbuild"):

    # init gcp client
    credentials, _ = default()
    client = storage.Client(credentials=credentials)

    # get private key from GCS bucket
    bucket = client.get_bucket("pipeline-ops")
    blob = bucket.get_blob(blob)

    return blob.download_as_text()


if __name__ == "__main__":
    # Replace these variables with your own values
    hostname = '34.101.36.18'
    username = 'cloud_build_ssh_key'
    # private_key_file = './ssh-private-key-cloudbuild'
    private_key_file = get_cloudbuild_private_key()

    # Establish SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load private key
    private_key = paramiko.RSAKey.from_private_key(StringIO(private_key_file))

    try:
        ssh.connect(hostname=hostname, username=username, pkey=private_key)
        print("connected to instance via SSH")

        sftp = ssh.open_sftp()
        dir_to_copy_list = ["dags", "data"]

        # loop over directories to copy
        for dir_name in dir_to_copy_list:
            local_dir = f"./{dir_name}/"
            remote_dir = f"/home/ragindafirdaus01/folder-x/{dir_name}/"
            
            # loop over files under each dir
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    if "__pycache__" not in root:
                        local_path = os.path.join(root, file)
                        remote_path = os.path.join(remote_dir, os.path.relpath(local_path, local_dir))
                        sftp.put(local_path, remote_path)
                        print(f"successfully copy file {str(os.path.join(root, file))} !")

    except paramiko.AuthenticationException:
        print("Authentication failed, please check your username and private key!")

    except paramiko.SSHException as e:
        print("Unable to establish SSH connection:", str(e))

    finally:
        sftp.close()
        ssh.close()