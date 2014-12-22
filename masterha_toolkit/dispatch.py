#!/usr/bin/env python

import sys
from argparse import ArgumentParser
from conf.config import GlobalConfig
from lib.dispatch.vip import DispatchManager

CONFIGPATH = "/etc/masterha_dispatcher/dispatcher.cnf"
def configure_argparse(parser):
    parser.add_argument('--command')
    parser.add_argument('--orig_master_host')
    parser.add_argument('--orig_master_ip')
    parser.add_argument('--orig_master_port')
    parser.add_argument('--orig_master_user')
    parser.add_argument('--orig_master_password')
    parser.add_argument('--orig_master_ssh_port')
    parser.add_argument('--orig_master_ssh_user')
    parser.add_argument('--new_master_host')
    parser.add_argument('--new_master_ip')
    parser.add_argument('--new_master_port')
    parser.add_argument('--new_master_user')
    parser.add_argument('--new_master_password')
    parser.add_argument('--new_master_ssh_port')
    parser.add_argument('--new_master_ssh_user')
    parser.add_argument('--ssh_user')
    parser.add_argument('--ssh_options')
    parser.add_argument('--orig_master_is_new_slave', action='store_true')

def main():
    parser = ArgumentParser()
    configure_argparse(parser)
    args = parser.parse_args()

    c = GlobalConfig(CONFIGPATH)
    print c.config

    dispatch = DispatchManager(c, args)
    if dispatch.execute():
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
