import datetime
import pytz
import json
import mysql.connector
import twitter_updater


def return_coords(coords):
    try:
        return str(coords['geometry']['coordinates'])
    except:
        return ""


def convert_date_utc(date_str):
    date_str = str(date_str)

    if date_str == 'None':
        pass
    else:
        date_str = date_str.replace('+00:00', '+0000')
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return dt.astimezone(pytz.utc)


def mysql_select_existing_alerts(config):
    try:
        con = mysql.connector.connect(user=config.get("mysql", "username"), password=config.get("mysql", "password"),
                                      host=config.get("mysql", "host"), database=config.get("mysql", "database"),
                                      port=config.get("mysql", "port"), use_pure=True)
        cur = con.cursor()

        qry = "SELECT `noaa_id` FROM `NSWN`.`NWS_Test_Alerts`"
        cur.execute(qry)
        res = cur.fetchall()
        cur.close()
        return res

    except mysql.connector.Error as err:
        print(str(err))


def check_for_new_alerts(alerts, config):
    alerts_stored = mysql_select_existing_alerts(config)

    def check_if_exist(alert_id):
        for stored_alert in alerts_stored:
            if str(stored_alert[0]) == str(alert_id):
                return True
            else:
                pass

        return False

    for alert in alerts:
        if check_if_exist(alert['properties']['id']):
            pass
        else:
            mysql_insert_alert(alert, config)
            twitter_updater.main(config, alert)


def mysql_insert_alert(alert, config):
    try:
        con = mysql.connector.connect(user=config.get("mysql", "username"), password=config.get("mysql", "password"),
                                      host=config.get("mysql", "host"), database=config.get("mysql", "database"),
                                      port=config.get("mysql", "port"), use_pure=True)
        cur = con.cursor()
        prepared_cursor = con.cursor(prepared=True)

        stmt_insert = "INSERT INTO `NSWN`.`NWS_Test_Alerts` (`noaa_id`, `areaDesc`, `geocode_UGC`, `geocode_SAME`, " \
                      "`sent`, `effective`, `onset`, `expires`, `ends`, `status`, `messageType`, `category`, " \
                      "`severity`, `certainty`, `urgency`, `event`, `senderName`, `headline`, `description`, " \
                      "`instruction`, `response`, `geometry`,`raw_sent`,`raw_effective`,`raw_onset`,`raw_expires`," \
                      "`raw_ends`)"
        stmt_values = "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s," \
                      " %s, %s, %s, %s, %s)"
        args = (alert['properties']['id'], alert['properties']['areaDesc'], str(alert['properties']['geocode']['UGC']),
                str(alert['properties']['geocode']['SAME']), convert_date_utc(alert['properties']['sent']),
                convert_date_utc(alert['properties']['effective']), convert_date_utc(alert['properties']['onset']),
                convert_date_utc(alert['properties']['expires']), convert_date_utc(alert['properties']['ends']),
                alert['properties']['status'], alert['properties']['messageType'], alert['properties']['category'],
                alert['properties']['severity'], alert['properties']['certainty'], alert['properties']['urgency'],
                alert['properties']['event'], alert['properties']['senderName'], alert['properties']['headline'],
                alert['properties']['description'], alert['properties']['instruction'], alert['properties']['response'],
                return_coords(alert), alert['properties']['sent'], alert['properties']['effective'],
                alert['properties']['onset'], alert['properties']['expires'], alert['properties']['ends'])

        try:
            if alert['properties']['event'] == "Test Message":
                pass
            else:
                prepared_cursor.execute("{} {}".format(stmt_insert, stmt_values), args)
                print("{} - {}".format(alert['properties']['headline'], alert['properties']['id']))
                cur.execute("commit;")
                cur.close()
                prepared_cursor.close()
        except mysql.connector.Error as err:
            cur.close()
            prepared_cursor.close()
            print("ERR: {} MSG: {}".format(err.errno, err.msg))

    except mysql.connector.Error as err:
        print(str(err))


def get_alerts_json(api_url, request):
    req = request("GET", api_url).text
    alerts = json.loads(req)

    return alerts["features"]


def main(config, request):
    alerts = get_alerts_json(config.get("noaa", "api_url"), request)
    check_for_new_alerts(alerts, config)


if __name__ == "__main__":
    from sys import argv
    from configparser import ConfigParser
    from os import path
    from requests import request

    config_file = path.abspath(argv[1])
    config_parse = ConfigParser()
    config_parse.read(config_file)

    main(config_parse, request)
