def mysql_insert(alert):
    pass

def store_alerts(alert_dict):
    pass


def get_alerts_json(api_url):
    from requests import request
    from json import loads

    req = request("GET",api_url).text
    alerts = loads(req)

    return alerts["features"]

def main(config):
    alerts = get_alerts_json(config.get("noaa","api_url"))

    for alert in dict(alerts):
        print(alert)


if __name__ == "__main__":
    from sys import argv
    from configparser import ConfigParser
    from os import path

    config_file = path.abspath(argv[1])
    config_parse = ConfigParser()
    config_parse.read(config_file)

    main(config_parse)