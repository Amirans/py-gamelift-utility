import boto3
import sys
import os
from requests import get
from pathlib import Path
from botocore.exceptions import ClientError

client = boto3.client('gamelift')


def create_output_dir(path_dir):
    try:
        Path(path_dir).mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Failed to Create path {path_dir} Due to {e}")


def list_fleets(build_id):
    """ Attempts to retrieve a list of fleets associated with the given a build
    :param build_id: describes the id of the build to return the associated fleets
    :return: list of fleets
    """
    response = client.list_fleets(
        BuildId=build_id
    )

    if "FleetIds" not in response or len(response["FleetIds"]) == 0:
        sys.exit(f"No Fleets Associated With Build Id {build_id}")
    else:
        return response["FleetIds"]


def describe_instances(fleet_id):
    """ Retrieves information about a fleet's instances, including instance IDs, connection data, and status. 
    :param fleet_id: describes the id of the fleet to return the associated instances
    :return: list of dict instances
    """
    describeInstancesResponse = client.describe_instances(
        FleetId=fleet_id
    )

    if "Instances" not in describeInstancesResponse or len(describeInstancesResponse["Instances"]) == 0:
        print(f"Fleet {fleet_id} Has No Active Instances")
        return []

    return describeInstancesResponse["Instances"]


def get_instance_os(instance):
    return "LINUX" if instance["OperatingSystem"].count("LINUX") > 0 else "WINDOWS"


def update_fleet_port(fleet_id, fleet_instances, public_ip):
    """ Updates permissions that allow inbound traffic to connect to game sessions that are being hosted on instances in the fleet.. 
    :param fleet_id: describes the id of the fleet to update the port settings for
    :param fleet_instances: List of Instance dicts
    :param public_ip: Public Ip of the Remote Access Instigator
    """
    has_linux_instances = False
    has_windows_instances = False
    inbound_permission = []

    for each_instance in fleet_instances:

        each_instance_os = get_instance_os(each_instance)

        if each_instance_os == "LINUX" and not has_linux_instances:
            has_linux_instances = True
            inbound_permission.append(
                {
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRange': public_ip + '/32',
                    'Protocol': 'TCP'
                }
            )
        elif each_instance_os == "WINDOWS" and not has_windows_instances:
            has_windows_instances = True
            inbound_permission.append(
                {
                    'FromPort': 3389,
                    'ToPort': 3389,
                    'IpRange': public_ip + '/32',
                    'Protocol': 'TCP'
                }
            )

    try:
        client.update_fleet_port_settings(
            FleetId=fleet_id,
            InboundPermissionAuthorizations=inbound_permission
        )
    except ClientError as e:
        print(e)


def get_remote_access(instance, output):

    instance_id = instance["InstanceId"]
    fleet_id = instance["FleetId"]
    print(
        f"Attempting to Get Instance Remote Access for Instance {instance_id}")

    # Get Remote Access Request
    getAccessResponse = client.get_instance_access(
        FleetId=fleet_id,
        InstanceId=instance_id
    )

    if "InstanceAccess" not in getAccessResponse:
        print(f"Failed to Get Instance Access for Instance {instance_id}")
        return

    instance_access = getAccessResponse["InstanceAccess"]

    instance_output_path = os.path.join(output, fleet_id, instance_id)

    create_output_dir(instance_output_path)

    # Save Credential Information
    with open(instance_output_path + "/Info.txt", 'w') as f:
        f.write("UserName:" +
                instance_access["Credentials"]["UserName"] + "\n")
        f.write("Secret/Password:" + instance_access["Credentials"]["Secret"])
        f.close()

    print(
        f"Saved Instance Remote Access for Instance {instance_id} at \"{instance_output_path}\"")

    # Save Credential Secret Key as Private Key for Linux Operating System
    if get_instance_os(instance) == "LINUX":
        with open(instance_output_path + "/PrivateKey.pem", 'w') as f:
            f.write(instance_access["Credentials"]["Secret"])
            f.close()
        print(
            f"Saved Secret Private Key for Instance {instance_id} at \"{instance_output_path}\"")


output_directory = input(f"Output Directory [{os.getcwd()}]: ") or os.getcwd()

create_output_dir(output_directory)

region_confirmation = input(
    f"Is Current AWS Region \"{boto3.session.Session().region_name}\" Correct: (y/n)") or 'y'

if not region_confirmation:
    sys.exit("Invalid Region Confirmation")
elif region_confirmation.lower() == 'n':
    sys.exit("Please Configure the AWS Region and Start Over")

while True:
    fleet_or_buid = input("Enter a Fleet Id or Build Id:")

    if not fleet_or_buid or fleet_or_buid.count('-', 0, 6) == 0:
        print("Please Enter a Valid Fleet ID or Build ID, Accepted Formats are fleet-### or build-### ")
    else:
        break

prefix = fleet_or_buid.split("-")[0].lower()

fleet_list = []

if prefix == "fleet":
    fleet_list.append(fleet_or_buid)
elif prefix == "build":
    fleet_list = list_fleets(fleet_or_buid)


instance_list = []

publicIp = get('https://api.ipify.org').text

if not publicIp:
    exit("Failed to Get Public IP")

for each_fleet_id in fleet_list:
    # Describe Fleet Instances
    this_fleet_instances = describe_instances(each_fleet_id)

    # Open the Port for SSH or RDP
    update_fleet_port(each_fleet_id, this_fleet_instances, publicIp)

    instance_list.extend(this_fleet_instances)

for each_instance in instance_list:
    get_remote_access(each_instance, output_directory)
