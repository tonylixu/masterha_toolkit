#!/usr/bin/env python

import sys
import os
import subprocess
import time
import logging

LOGGER = logging.getLogger(__name__)

class DispatchManager(object):

    """
    Generates a configuration for the vip dispatch method. Provides
    failover mechanism to evaluate masterha_ip_failover_script and
    masterha_ip_online_change_script calls from masterha_manager
    """
 
    @staticmethod
    def _execute_ssh(command, timeout=60):
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_delay = 0
        while p.poll() == None:
            time.sleep(1)
            command_delay += 1
            if command_delay >= timeout:
                LOGGER.critical("SSH execution timeout during failover. Failover process is in an unknown state.")
                LOGGER.debug("SSH Command: %s", command)
                p.stdout.close()
                p.stderr.close()
                sys.exit(os.EX_TEMPFAIL)

        (return_value, output, error) = (p.returncode, p.stdout.read(), p.stderr.read())
        p.stdout.close()
        p.stderr.close()
        return (return_value, output, error)
        

    def execute(self):
        """
        Perform a failover command passed from masterha_manager, where
        command is in (status, start, stop, stopssh).
        """
        LOGGER.info("Starting failover with command: %s", self.command)

        ssh_user = self.ssh["ssh_user"]
        if self.command == "status":
            if ssh_user is None:
		ssh_user = self.ssh["orig_master_ssh_user"]
            ssh_host = self.ssh["orig_master_host"]
	    ssh_command = "/sbin/ip a s dev %s" % (self.vip["interface"])
        elif self.command in ("stop", "stopssh"):
            if ssh_user is None:
		ssh_user = self.ssh["orig_master_ssh_user"]
            ssh_host = self.ssh["orig_master_host"]
	    ssh_command = "/sbin/ip a del %s/%s dev %s" % (self.vip["address"],
                                                           self.vip["subnet"], self.vip["interface"])
        elif self.command == "start":
            if ssh_user is None:
		ssh_user = self.ssh["new_master_ssh_user"]
            ssh_host = self.ssh["new_master_host"]
	    ssh_command = "/sbin/ip a add %s/%s dev %s" % (self.vip["address"],
							   self.vip["subnet"], self.vip["interface"])
        else:
            LOGGER.error("Invalid failover command flag passed, command = %s", self.command)
            sys.exit(os.EX_USAGE)

        if self.ssh["use_sudo"] == True:
            ssh_command = "/usr/bin/sudo " + ssh_command
        full_command = ["/usr/bin/ssh"] + self.ssh["ssh_options"].split() + \
                           ["-q"] + [ssh_user + "@" + ssh_host] + [ssh_command]
        (return_value, output, error) = self._execute_ssh(full_command, self.ssh["timeout"])
        
        if return_value == 0:
            LOGGER.debug("Failover SSH action returned with exit status 0 for command '%s'", self.command)
            if ssh_command == "status":
		if output.find(self.vip["address"] + "/" + str(self.vip["subnet"])) != -1:
                    LOGGER.debug("VIP %s/%s found on host '%s'", self.vip["address"],
                                 self.vip["subnet"], ssh_host)
		    return True
		else:
                    LOGGER.error("VIP %s/%s not found on host '%s'", self.vip["address"],
                                 self.vip["subnet"], ssh_host)
                    LOGGER.debug("SSH status command returned: %s", output)
		    return False
            return True
        else:
            LOGGER.error("Failover SSH action returned with exit status %s for command '%s'",
                         return_value, self.command)
            LOGGER.info("SSH stderr from host %s: %s", ssh_host, error)


    def __init__(self, c, args):
        config_spec = """
        [dispatch]
        vip_address             = ip_addr
        vip_subnet              = integer(8,32)
        vip_interface           = string
        use_sudo                = boolean(default=False)
        ssh_timeout             = integer(default=60)
        """.splitlines()
        c.add_dispatch(c.config["dispatcher"]["dispatch_method"], config_spec)

        self.command = args.command

        self.vip = {}
        self.vip["address"] = c.config["dispatch"]["vip_address"]
        self.vip["subnet"] = c.config["dispatch"]["vip_subnet"]
        self.vip["interface"] = c.config["dispatch"]["vip_interface"]

        self.ssh = {}
        for arg in ("orig_master_host", "ssh_user", "ssh_options",
                    "new_master_host", "orig_master_ssh_user", "new_master_ssh_user"):
            self.ssh[arg] = getattr(args, arg)
        self.ssh["use_sudo"] = c.config["dispatch"]["use_sudo"]
        self.ssh["timeout"] = c.config["dispatch"]["ssh_timeout"]
