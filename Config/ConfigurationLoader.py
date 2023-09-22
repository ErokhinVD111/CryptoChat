import configparser


class ConfigurationLoader:
    def __init__(self, path: str):
        config = configparser.ConfigParser()
        config.read(path)
        self.server = dict(config["Server"])
        self.message = dict(config["Message"])

    def print_all_configuration(self):
        print("server: ", self.server)
        print("message: ", self.message)
