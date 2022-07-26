import logging
import os

import pycloudlib
from pycloudlib.cloud import ImageType


def handle_ssh_key(ec2, key_name):
    """Manage ssh keys to be used in the instances."""
    if key_name in ec2.list_keys():
        ec2.delete_key(key_name)

    key_pair = ec2.client.create_key_pair(KeyName=key_name)
    private_key_path = "ec2-test.pem"
    with open(private_key_path, "w", encoding="utf-8") as stream:
        stream.write(key_pair["KeyMaterial"])
    os.chmod(private_key_path, 0o600)

    # Since we are using a pem file, we don't have distinct public and
    # private key paths
    ec2.use_key(
        public_key_path=private_key_path,
        private_key_path=private_key_path,
        name=key_name,
    )


def checks(instance):
    print(instance.execute("sudo ua status --wait"))
    print(instance.execute("sudo uname -r"))
    print(instance.execute("sudo cat /proc/sys/crypto/fips_enabled"))
    print(instance.execute("sudo cat /etc/apt/sources.list.d/*"))
    print(instance.execute("sudo ls /run/reboot-required*"))
    print(instance.execute("sudo cat /run/reboot-required.pkgs"))
    print(
        instance.execute(
            "sudo cat /var/lib/ubuntu-advantage/private/machine-token.json"
        )
    )
    print(instance.execute("sudo apt-cache policy"))
    print(instance.execute("sudo cloud-init query instance_id"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ec2 = pycloudlib.EC2(tag="examples")
    key_name = "test-ec2"
    handle_ssh_key(ec2, key_name)

    daily_pro = ec2.daily_image(release="focal", image_type=ImageType.PRO)

    print("Launching Pro instance...")
    instance = ec2.launch(daily_pro, instance_type="m5.large")
    instance.execute("touch custom_config_file")
    print(instance.execute("sudo ua status --wait"))
    print(instance.execute("sudo apt update"))
    print(instance.execute("sudo apt install ubuntu-advantage-tools"))

    print("")
    print("install ua version from main")
    print("")
    instance.push_file("./ua.deb", "/tmp/ua.deb")
    print(instance.execute("sudo dpkg -i /tmp/ua.deb"))
    instance.pull_file("/var/log/ubuntu-advantage.log", "./log")
    instance.pull_file("/var/log/ubuntu-advantage.log", "./log")

    print("")
    print("enable fips-updates")
    print("")
    print(instance.execute("sudo ua enable fips-updates --assume-yes"))
    instance.pull_file("/var/log/ubuntu-advantage.log", "./log")

    checks(instance)

    print("")
    print("snapshotting")
    print("")
    image = ec2.snapshot(instance)

    print("")
    print("launching clone and checking status")
    print("")
    new_instance = ec2.launch(image, instance_type="m5.large")
    instance.pull_file("/var/log/ubuntu-advantage.log", "./log")

    checks(new_instance)

    print("")
    print("Deleting Pro instances and image")
    print("")
    new_instance.delete()
    ec2.delete_image(image)
    instance.delete()
