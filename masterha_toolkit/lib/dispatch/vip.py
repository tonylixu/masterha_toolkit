#!/usr/bin/env python

import subprocess
import time

class DispatchManager(object):

    def _remove_vip(self, ssh_host, ssh_user, ssh_options, use_sudo, vip_ip, vip_subnet, vip_interface):
        ssh_command = "/sbin/ip a del %s/%s dev %s" % (vip_ip, vip_subnet, vip_interface)
        command = self._prepare_ssh(ssh_host, ssh_user, ssh_options, ssh_command, use_sudo)
        (return_value, output, error) = self._execute_ssh(command)
        return True if return_value == 0 else False
        
    def _add_vip(self, ssh_host, ssh_user, ssh_options, use_sudo, vip_ip, vip_subnet, vip_interface):
        ssh_command = "/sbin/ip a add %s/%s dev %s" % (vip_ip, vip_subnet, vip_interface)
        command = self._prepare_ssh(ssh_host, ssh_user, ssh_options, ssh_command, use_sudo)
        (return_value, output, error) = self._execute_ssh(command)
        return True if return_value == 0 else False

    def _check_vip(self, ssh_host, ssh_user, ssh_options, use_sudo, vip_ip, vip_subnet, vip_interface):
        ssh_command = "/sbin/ip a s dev %s" % (vip_interface)
        command = self._prepare_ssh(ssh_host, ssh_user, ssh_options, ssh_command, use_sudo)
        (return_value, output, error) = self._execute_ssh(command)
        if output.find(vip_ip + "/" + vip_subnet) != -1:
            return True
        else:
            return False
 
    @staticmethod
    def _execute_ssh(command):
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_delay = 0
        while p.poll() == None:
            time.sleep(1)
            command_delay += 1
            if command_delay >= 60:
                # TODO: Allow timeout to be set in config
                break

        (return_value, output, error) = (p.returncode, p.stdout.read(), p.stderr.read())
        p.stdout.close()
        p.stderr.close()
        return (return_value, output, error)
        
    @staticmethod
    def _prepare_ssh(ssh_host, ssh_user, ssh_options, ssh_command, use_sudo):
        if use_sudo == True:
            ssh_command = "/usr/bin/sudo " + ssh_command
        command = ["/usr/bin/ssh"] + ssh_options.split() + ["-q"] + [ssh_user + "@" + ssh_host] + [ssh_command]
        return command

    def execute(self):
        ssh_user = self.ssh["ssh_user"]
        if self.command == "status":
            return self._check_vip(self.ssh["orig_master_host"], ssh_user,
                                   self.ssh["ssh_options"], self.ssh["use_sudo"],
                                   self.vip["address"], self.vip["subnet"], self.vip["interface"])
        elif self.command in ("stop", "stopssh"):
            if ssh_user == None:
                ssh_user = self.ssh["orig_master_ssh_user"]
            return self._remove_vip(self.ssh["orig_master_host"], ssh_user,
                                    self.ssh["ssh_options"], self.ssh["use_sudo"],
                                    self.vip["address"], self.vip["subnet"], self.vip["interface"])
        elif self.command == "start":
            if ssh_user == None:
                ssh_user = self.ssh["new_master_ssh_user"]
            return self._add_vip(self.ssh["new_master_host"], ssh_user,
                                 self.ssh["ssh_options"], self.ssh["use_sudo"],
                                 self.vip["address"], self.vip["subnet"], self.vip["interface"])
        
    def __init__(self, c, args):
        self.command = args.command
        self.ssh = {}
        for arg in ("orig_master_host", "orig_master_ip",
                    "ssh_user", "ssh_options", "new_master_host",
                    "orig_master_ssh_user", "new_master_ssh_user"):
            self.ssh[arg] = getattr(args, arg)
        if c.config["dispatch"]["use_sudo"] in ("yes", "y", 1, "True", True):
            self.ssh["use_sudo"] = True
        else:
            self.ssh["use_sudo"] = False

        self.vip = {}
        self.vip["address"] = c.config["dispatch"]["vip_address"]
        self.vip["subnet"] = c.config["dispatch"]["vip_subnet"]
        self.vip["interface"] = c.config["dispatch"]["vip_interface"]
