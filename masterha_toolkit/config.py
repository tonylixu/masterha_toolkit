import os
import sys
import logging
from configobj import ConfigObj
from validate import Validator

LOGGER = logging.getLogger(__name__)

class GlobalConfig(object):

    """
    Provides support for global and dispatch configuration files.
    Use ConfigObj and Validator to generate a dictionary of
    all available configuration options.
    """

    def _add_config(self, config_file, config_spec, validator=None):
        self._test_file(config_file)
        if validator == None:
            val = Validator()
        else:
            val = Validator(validator)
	new_config = ConfigObj(config_file, configspec=config_spec)
        validation_success = new_config.validate(val)
        if validation_success != True:
            LOGGER.error("Config validation for %s failed", config_file)
            LOGGER.debug("configspec used for validation: %s", config_spec)
            sys.exit(os.EX_CONFIG)
        self.config.update(new_config.dict())

    @staticmethod
    def _test_file(config_file):
        if not os.path.isfile(config_file):
            if os.path.exists(config_file):
                LOGGER.error("Configuration path exists but is not a file: %s", config_file)
		sys.exit(os.EX_IOERR)
            else:
                LOGGER.error("Configuration file not found: %s", config_file)
		sys.exit(os.EX_IOERR)
        
    def add_dispatch(self, dispatch_method, config_spec, validator=None):
        """
        Add dispatch configuration defined in global:dispatch_method
        """
        config_file = os.path.join(self.config_dir, 'dispatch', dispatch_method) + ".cnf"
        self._add_config(config_file, config_spec)
        
    def __init__(self, config_file):
        config_file = os.path.abspath(config_file)
        self.config_dir = os.path.dirname(config_file)

        self.config = {}
	config_spec = """
	[dispatcher]
	dispatch_method         = string
	mha_cluster_conf        = string(default=None)
	report_email            = string(default=None)
        log_file                = string(default=None)
	""".splitlines()
        self._add_config(config_file, config_spec)
