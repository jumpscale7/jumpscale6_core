from libcloud.compute.providers import get_driver
from JumpScale import j
import JumpScale.baselib.remote

class AmazonProvider(object):

    def __init__(self):
        self._region = None
        self._client = None

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        self._region = 'ec2_%s' % value

    def connect(self, access_key_id, secret_access_key):
        if not self.region:
            raise RuntimeError('Region must be set first')
        self._client = get_driver(self.region)(access_key_id, secret_access_key)

    def find_size(self, size_id):
        return [s for s in self._client.list_sizes(self.region) if s.id.find(size_id) != -1]

    def find_image(self, image_id):
        return [i for i in self._client.list_images(self.region) if i.id.find(image_id) != -1]

    def list_machines(self):
        result = list()
        machines = self._client.list_nodes()
        for machine in machines:
            data = dict()
            data['id'] = machine.id
            data['name'] = machine.name
            data['public_ips'] = machine.public_ips
            data['private_ips'] = machine.private_ips
            data['image_id'] = machine.extra['imageId']
            data['status'] = machine.extra['status']
            data['size_id'] = machine.extra['instancetype']
            result.append(data)
        return result

    def create_machine(self, name, image, size, aws_ssh_key):
        return self._client.create_node(name=name, image=image, size=size, ex_keyname=aws_ssh_key)

    def execute_command(self, machine_name, command, sudo=False):
        machines = self.list_machines()
        host = None
        for machine in machines:
            if machine['name'] == machine_name:
                host = machine['public_ips'][0]
                break

        if not host:
            raise RuntimeError('Could not find machine: %s' % machine_name)
        rapi = j.remote.cuisine.api
        rapi.connect(host, user='ubuntu')
        if sudo:
            return rapi.sudo(command)
        return rapi.run(command)