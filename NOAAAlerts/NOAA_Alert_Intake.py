import requests
import configparser
import json
import mysql.connector
import sys
import time
import datetime


def add_to_db(config):
    try:
        conn = mysql.connector.connect(user=config['mysql']['username'], password=config['mysql']['password'],
                                       host=config['mysql']['host'], database=config['mysql']['database'],
                                       port=config['mysql']['port'], use_pure=True)

        cur = conn.cursor()
        preCur = conn.cursor(prepared=True)

    except mysql.connector.Error as err:
        print(str(err))


def get_alerts(api_url):
    alerts = json.loads(requests.get(api_url).text)
    return alerts


def main():
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    text = get_alerts(config.get("noaa", "api_url"))

    for f in text["features"]:
        print(f['id'])


if __name__ == "__main__":
    main()
