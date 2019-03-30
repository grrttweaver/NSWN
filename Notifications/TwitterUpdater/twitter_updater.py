
def get_alerts_json(api_url):


def main(config):
    print(config.get("noaa","api_url"))


if __name__ == "__main__":
    from sys import argv
    from configparser import ConfigParser
    from os import path

    config_file = path.abspath(argv[1])
    config_parse = ConfigParser()
    config_parse.read(config_file)

    main(config_parse)
