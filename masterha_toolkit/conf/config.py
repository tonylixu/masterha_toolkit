import os
from configobj import ConfigObj
from validate import Validator

class GlobalConfig(object):

    def _parse_config(self, config_file, config_spec,
                      required_keys, validator):
        if validator == None:
            val = Validator()
        else:
            val = Validator(validator)
        if os.path.isfile(config_file):
            config = ConfigObj(config_file, configspec=config_spec)
        else:
            config = ConfigObj(None, configspec=config_spec)
        if config_spec is not None:
            if not config.validate(val):
		return 1
	    for key in required_keys:
		if key not in config.dict():
		    return 1
		elif required_keys[key] not in config[key]:
		    return 1
        return config.dict()

    def _add_config(self, config_file, config_spec=None,
                   required_keys=None, validator=None):
        new_config = self._parse_config(config_file, config_spec,
                                        required_keys, validator)
        self.config.update(new_config)

    def _add_dispatch(self, dispatch_method, config_spec=None,
                      required_keys=None, validator=None):
        config_file = os.path.join(self.config_dir, 'dispatch',
                                   dispatch_method) + ".cnf"
        self._add_config(config_file)
        
    def __init__(self, config_file):
        self.config = {}
        config_file = os.path.abspath(config_file)
        self.config_dir = os.path.dirname(config_file)
	config_spec = """
	[dispatcher]
	dispatch_method         = string(default=None)
	mha_cluster_conf        = string(default=None)
	report_email            = string(default=None)
	""".splitlines()
	required_keys = { "dispatcher" : "dispatch_method" }
        
        self._add_config(config_file, config_spec, required_keys)
        self._add_dispatch(self.config["dispatcher"]["dispatch_method"])
