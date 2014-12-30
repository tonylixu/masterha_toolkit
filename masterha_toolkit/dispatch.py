#!/usr/bin/env python

import sys
import logging
from argparse import ArgumentParser
from masterha_toolkit.config import GlobalConfig
from masterha_toolkit.dispatches.vip import DispatchManager

CONFIGPATH = "/etc/masterha_dispatcher/dispatcher.cnf"
DEFAULT_LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DEFAULT_LOG_LEVEL = logging.INFO

LOGGER = logging.getLogger(__name__)

def configure_argparse(parser):
    parser.add_argument('--command', required=True, help='Dispatch action (status, stop, stopssh, start)')
    parser.add_argument('--orig_master_host', help='Original server hostname')
    parser.add_argument('--orig_master_ip', help='Original server IP')
    parser.add_argument('--orig_master_port', help='Original master MySQL port')
    parser.add_argument('--orig_master_user', help='Original master MySQL user')
    parser.add_argument('--orig_master_password', help='Original master MySQL password')
    parser.add_argument('--orig_master_ssh_port', help='Original master SSH port')
    parser.add_argument('--orig_master_ssh_user', help='Original master SSH user')
    parser.add_argument('--new_master_host', help='New master hostname')
    parser.add_argument('--new_master_ip', help='New master IP')
    parser.add_argument('--new_master_port', help='New master MySQL port')
    parser.add_argument('--new_master_user', help='New master MySQL user')
    parser.add_argument('--new_master_password', help='New master MySQL password')
    parser.add_argument('--new_master_ssh_port', help='New master SSH port')
    parser.add_argument('--new_master_ssh_user', help='New master SSH user')
    parser.add_argument('--ssh_user', help='Global SSH user')
    parser.add_argument('--ssh_options', help='SSH arguments')
    parser.add_argument('--orig_master_is_new_slave', action='store_true', help='Leave old master in pool during manual failover')


def configure_logging(filename=None, level=None):
    root = logging.getLogger()
    if not filename:
        filename = "/var/log/masterha_dispatcher.log"
    if not level:
        level = logging.DEBUG
    root.setLevel(level)
    handler = logging.FileHandler(filename, "a", encoding="utf8")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)


def main():
    configure_logging()
    parser = ArgumentParser()
    configure_argparse(parser)
    args = parser.parse_args()

    c = GlobalConfig(CONFIGPATH)
    LOGGER.info("MasterHA Dispatcher started")
    dispatch = DispatchManager(c, args)
    if dispatch.execute():
        LOGGER.info("MasterHA Dispatcher completed successfully")
        return 0
    else:
        LOGGER.error("MasterHA Dispatcher completed with errors")
        return 1

if __name__ == '__main__':
    sys.exit(main())
