import os

class ConfigKeyException(Exception):
    """
    Exception that is raised if the key is not in the dictionary thus not in the configuration file.
    """
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return "No such Key in the configuration file"


class ConfReader:
    """
    This class is a parser for a configuration file. It reads the keys and values of the file and write them in a dictionary.
    The configuration file must be written as follows: KEY = Value and a line unused or a commentary must strart with a #
    """

    def __init__(self, filename, path='./'):
        """
        Simple constructor for the object
        :param filename: name of the configuration file
        :param path: path of the configuration file, by default, it is the current folder
        """
        self.path = os.path.join(path, filename)
        self.conf = {}
        self.parse_values()

    def parse_values(self):
        """
        This method reads the configuration file and stores the data in a dictionary
        :return:
        """
        with open(self.path) as conf_file:
            lines = conf_file.readlines()
            for line_conf in lines:
                if not line_conf.startswith("#"):
                    self.conf[line_conf.split("=")[0].strip('\n').strip("\r").strip()] = line_conf.split("=")[1].strip('\n').strip("\r").strip()
        return True

    def get_value(self, key):
        """
        :param key: Item of the configuration file
        :return: the value associated to 'key' in the config file
        """
        try:
            return self.conf[key]
        except KeyError:
            raise ConfigKeyException
