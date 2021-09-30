# Vmfinder CLI for BOSH, TKGI

VM finder is a wrapper for TKGI and BOSH clients

#Installation
bash install.sh

#Usage

usage: vmfinder [-h] [-c CLUSTER_NAME] [-i VM_IP] [-p POD_IP]

Return aliases of all the subscribers of a list.

optional arguments:
  -h, --help            show this help message and exit
  -c CLUSTER_NAME, --cluster-name CLUSTER_NAME
                        Tkgi cluster name (default: None)
  -i VM_IP, --from-ip VM_IP
                        Ip of VM (default: None)
  -p POD_IP, --from-pod-ip POD_IP
                        Ip of POD (default: None)  

# Examples

#### List cluster vms
vmfinder -c CLUSTER_NAME
#### Get example commands via VM ip to interact with bosh
vmfinder -i VM_IP
#### Get example commands via Pod ip to interact with bosh 
vmfinder -p POD_IP
