import paramiko
from io import StringIO
import os
from google.auth import default
from google.cloud import storage

# define constant
REMOTE_HOSTNAME = "34.101.149.62"
REMOTE_USERNAME = "cloud_build_ssh_key"
REMOTE_PATH_MAIN_FOLDER = "/home/ragindafirdaus01/setup-airflow"
DIR_TO_UPDATE = ["data", "dags"]

def get_cloudbuild_private_key(blob="creds/ssh-key-cloudbuild"):

    # init gcp client
    credentials, _ = default()
    client = storage.Client(credentials=credentials)

    # get private key from GCS bucket
    bucket = client.get_bucket("pipeline-ops")
    blob = bucket.get_blob(blob)

    return blob.download_as_text()


if __name__ == "__main__":
    
    private_key_file = get_cloudbuild_private_key()

    # Establish SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load private key
    private_key = paramiko.RSAKey.from_private_key(StringIO(private_key_file))

    try:
        ssh.connect(hostname=REMOTE_HOSTNAME, username=REMOTE_USERNAME, pkey=private_key)
        print("connected to instance via SSH")

        sftp = ssh.open_sftp()

        print("[------------ update remote files begin ------------]")
        
        # loop over directories to copy
        for dir_name in DIR_TO_UPDATE:
            local_dir = f"../{dir_name}/"
            remote_dir = f"{REMOTE_PATH_MAIN_FOLDER}/{dir_name}/"

            # loop over files under remote dir, then delete all
            file_in_remote_dir_list = sftp.listdir(path=remote_dir)
            for file in file_in_remote_dir_list:
                sftp.remove(remote_dir+file)
            
            # # loop over files under local dir, then copy to remote dir
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    if "__pycache__" not in root:
                        local_path = os.path.join(root, file)
                        remote_path = os.path.join(remote_dir, os.path.relpath(local_path, local_dir))
                        sftp.put(local_path, remote_path)
                        print(f"successfully copy file {str(os.path.join(root, file))} !")
        
        print("[------------ update remote files completed ------------]")

        sftp.close()
        ssh.close()

    except Exception as e:
        raise (e)
