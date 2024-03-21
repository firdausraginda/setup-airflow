import paramiko


# Replace these variables with your own values
hostname = '34.101.36.18'
username = 'cloud_build_ssh_key'
private_key_file = '/Users/agi/Desktop/private-key-cloud-build'

# Establish SSH connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Load private key
private_key = paramiko.RSAKey.from_private_key_file(private_key_file)

try:
    ssh.connect(hostname=hostname, username=username, pkey=private_key)
    print("Connected to instance via SSH.")

    sftp = ssh.open_sftp()
    sftp.put('./dags/', '/home/ragindafirdaus01/folder-x/')

except paramiko.AuthenticationException:
    print("Authentication failed, please check your username and private key.")

except paramiko.SSHException as e:
    print("Unable to establish SSH connection:", str(e))

finally:
    sftp.close()
    ssh.close()