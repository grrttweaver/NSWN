import configparser
import json
import mysql.connector
import requests
import time
import datetime

config = configparser.ConfigParser()
config.read('../NSWN_Config.ini')


def logToFile(line):
    log_file = open("NOAA_Alerts.log", "a+")
    log_file.write(line)
    log_file.write("\n")
    log_file.flush()
    log_file.close()
    return line


try:
    conn = mysql.connector.connect(user=config['mysql']['username'], password=config['mysql']['password'], host=config['mysql']['host'], database=config['mysql']['database'],
                                   port=config['mysql']['port'])

    cur = conn.cursor()
    preCur = conn.cursor(prepared=True)

except mysql.connector.Error as err:
    print(logToFile(str(err)))

url = config.get("noaa","api_url")

looper = True
loopCount = 0
toIgnore = {}
while(looper):
    resp = requests.get(url)
    if resp == 200:
        print(resp.status_code)
    else:
        try:
            payload = json.loads(resp.text)
        except Exception as json_err:
            print(json_err.message)
            logToFile(json_err.message)
        feature = payload['features']
        severeAlerts = []
    for alert in feature:
        item = alert['properties']
        if item['messageType'] == 'Alert':
            severeAlerts.append(item)

    for d_alert in severeAlerts:
        isPresent = 0
        arr = []
        for string in d_alert['geocode']['UGC']:
            arr.append(str(string))

        count = "SELECT count(*) FROM Alerts WHERE noaa_id='{}'".format(d_alert['id'])

        try:
            cur.execute(count)
            row = cur.fetchall()
            isPresent = row[0]
            isPresent = isPresent[0]
        except mysql.connector.Error as err:
            if err.errno != 1062:
                print("*****{}".format(err))
                looper = False
                looperCount = 0
                print("\n COUNT: isPresent is: {}".format(isPresent))
                print(sql)
            else:
                pass

        if isPresent < 1:
            if d_alert['id'] in toIgnore:
                pass

            sql = "INSERT INTO `NSWN`.`Alerts` (`noaa_id`, `polygonCoords`, `event`, `severity`, `nws_office`," \
                  " `area_desc`, `onset`, `expires`, `headline`, `description`, `instruction`, `UGC_Codes`) " \
                  "VALUES (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")"
            data = (str(d_alert['id']), str("null"), str(d_alert['event']), str(d_alert['severity']), str(d_alert['senderName']),
                    str(d_alert['areaDesc']), str(d_alert['onset']), str(d_alert['expires']), str(d_alert['headline']).replace("\"",""),
                    str(d_alert['description']).replace("\"",""), str(d_alert['instruction']).replace("\"",""), arr)
            try:
                if d_alert['event'] == "Test Message":
                    pass
                else:
                    preCur.execute(sql % data)
                    cur.execute("commit;")
                    print("{}".format(d_alert['headline']))
            except mysql.connector.Error as err:
                if err.errno != 10600002:
                    print("*****{}".format(err))
                    # looper = False
                    if d_alert['id'] not in toIgnore:
                        print(sql % data)
                    print(d_alert['id'])
                    print("-------------------------------------")
                    toIgnore[d_alert['id']] = d_alert['id']
                    pass

                else:
                    print(err)
                    pass
        else:
            pass
        if loopCount > 1:
           time.sleep(3)

    print("Loop Count: {} - {}\n*/=*/=*/=*/=*/=*/=*/=*/=*/=*/=*/=*/=*/=*/=*/=*/=\n".format(loopCount,datetime.datetime.now()))

    loopCount += 1

conn.close()
