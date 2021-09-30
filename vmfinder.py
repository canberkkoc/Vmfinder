#!/usr/bin/python3
# coding: utf8

'''
VM finder wrapper for TKGI and BOSH clients
'''

import argparse
import json
import logging
import subprocess
from typing import Union, Tuple

logger = logging.getLogger("d")
logger.setLevel(logging.DEBUG)


class bcolors():
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Return aliases of all the subscribers of a list.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--cluster-name",
                        dest="cluster_name",
                        type=str,
                        help="Tkgi cluster name",
                        required=False)
    parser.add_argument("-i", "--from-ip",
                        dest="vm_ip",
                        type=str,
                        help="Ip of VM",
                        required=False)
    parser.add_argument("-p", "--from-pod-ip",
                        dest="pod_ip",
                        type=str,
                        help="Ip of Pod",
                        required=False)

    return parser.parse_args()


def process_modifier(command: str, jsonify: bool = True) -> Union[dict, str, list]:
    std_out = subprocess.run(command, shell=True, capture_output=True)
    if std_out.returncode > 0:
        return {}
    if jsonify:
        return json.loads(std_out.stdout.decode("utf-8"))
    return std_out.stdout.decode("utf-8")


def kubectl_commands(pod_ip: str) -> Union[Tuple[str, str], None]:
    contexts: list = str(process_modifier(command='kubectl config get-contexts -o name', jsonify=False)).split("\n")
    contexts.remove('')
    for i in contexts:
        std_out = process_modifier(f'kubectl get pods --context={i} -A  -o wide  -o json')
        if not std_out:
            print(f"{bcolors.BOLD}{bcolors.FAIL}CLUSTER:{bcolors.ENDC} {i.upper()} CAN NOT BE REACHED !!")
            continue
        pods_of_cluster: list = std_out.get("items")

        for j in pods_of_cluster:
            if j.get('status').get('podIP') == pod_ip:
                vm_of_pod: str = j.get('spec').get("nodeName")
                ip_of_vm: str = process_modifier(f'kubectl get nodes --context={i} {vm_of_pod}  -o wide  -o json').get(
                    'metadata').get("labels").get("spec.ip")
                return ip_of_vm, i
    return None


def tkgi_commands(cluster_name: str = "") -> dict:
    if cluster_name:
        tkgi_result = process_modifier(f'tkgi cluster {cluster_name} --json')
    else:
        tkgi_result = process_modifier(f'tkgi clusters --json')

    return tkgi_result


def bosh_commands(service_instance: str) -> dict:
    return process_modifier(f'bosh vms -d  {service_instance} --json')


def finder(cluster_name: str = "", vm_ip: str = "", pod_ip: str = "") -> None:
    if cluster_name:
        print(
            f'{bcolors.BOLD}{bcolors.UNDERLINE}{bcolors.FAIL}VM List for {cluster_name.upper()}'
            f'{bcolors.ENDC}'.center(125))
        for i in \
                bosh_commands(f'service-instance_{tkgi_commands(cluster_name=cluster_name).get("uuid")}').get("Tables")[
                    0].get(
                    "Rows"):
            print(
                f"{bcolors.BOLD}{bcolors.WARNING}Instance:{bcolors.ENDC} {i.get('instance')} -- "
                f"{bcolors.BOLD}{bcolors.WARNING}IP:{bcolors.ENDC} {i.get('ips')} -- "
                f"{bcolors.BOLD}{bcolors.WARNING}CID:{bcolors.ENDC} {i.get('vm_cid')}")
    else:
        if pod_ip:
            vm_ip = kubectl_commands(pod_ip=pod_ip)[0]
        for i in tkgi_commands():
            for j in bosh_commands(f'service-instance_{i.get("uuid")}').get("Tables")[0].get("Rows"):
                if j.get('ips') == vm_ip:
                    print(f'{bcolors.BOLD}{bcolors.UNDERLINE}{bcolors.FAIL}VM INFO{bcolors.ENDC}'.center(125))
                    print(
                        f"{bcolors.BOLD}{bcolors.WARNING}Cluster:{bcolors.ENDC} {i.get('name').upper()} -- "
                        f"{bcolors.BOLD}{bcolors.WARNING}Instance:{bcolors.ENDC} {j.get('instance')} -- "
                        f"{bcolors.BOLD}{bcolors.WARNING}IP:{bcolors.ENDC} {j.get('ips')} -- "
                        f"{bcolors.BOLD}{bcolors.WARNING}CID:{bcolors.ENDC} {j.get('vm_cid')}")
                    print(200 * "-")
                    print(f'{bcolors.BOLD}{bcolors.UNDERLINE}{bcolors.FAIL}EXAMPLE COMMANDS{bcolors.ENDC}'.center(125))
                    print(f'{bcolors.BOLD}{bcolors.OKCYAN}bosh -d  '
                          f'service-instance_{i.get("uuid")} ssh {j.get("instance")}{bcolors.ENDC}')
                    print(f'{bcolors.BOLD}{bcolors.OKCYAN}bosh -d  '
                          f'service-instance_{i.get("uuid")} delete-vm {j.get("vm_cid")}{bcolors.ENDC}')
                    return


if __name__ == '__main__':
    args = parse_args()
    if args.cluster_name:
        finder(cluster_name=args.cluster_name)
    elif args.vm_ip:
        finder(vm_ip=args.vm_ip)
    elif args.pod_ip:
        finder(pod_ip=args.pod_ip)
