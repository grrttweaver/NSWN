#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals
import mysql.connector, requests, json, time, configparser

config = configparser.ConfigParser()
config.read('../NSWN_Config.ini')


try:
    conn = mysql.connector.connect(user=config['mysql']['username'], password=config['mysql']['password'], host=config['mysql']['host'], database=config['mysql']['database'],
                                   port=config['mysql']['port'])

    cur = conn.cursor()
    preCur = conn.cursor(prepared=True)

except mysql.connector.Error as err:
    print err

url = "https://api.weather.gov/alerts/active"

looper = True
loopCount = 0
while(looper):
    resp = requests.get(url)
    if resp == 200:
        print resp.status_code
    else:
        payload = json.loads(resp.text)
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
                print "*****{}".format(err)
                looper = False
                looperCount = 0;
                print "\n COUNT: isPresent is: {}".format(isPresent)
                print sql
            else:
                pass

        if isPresent < 1:
            # sql = "INSERT INTO `NSWN`.`Alerts` (`noaa_id`, `polygonCoords`, `event`, `severity`, `nws_office`, " \
            #       "`area_desc`, `onset`, `expires`, `headline`, `description`, `instruction`, `UGC_Codes`) " \
            #       "VALUES ('{}', '{}', '{}', '{}', '{}', \"{}\", '{}', '{}', \"{}\", \"{}\", \"{}\", \"{}\");".format(
            #     d_alert['id'],"null",d_alert['event'],d_alert['severity'],d_alert['senderName'], d_alert['areaDesc'],
            #     d_alert['onset'],d_alert['expires'],d_alert['headline'],d_alert['description'],d_alert['instruction'],
            #     arr);
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
                    print "{}".format(d_alert['headline'])
            except mysql.connector.Error as err:
                if err.errno != 10600002:
                    print "*****{}".format(err)
                    looper = False
                    print sql % data
                    print "-------------------------------------"
                else:
                    pass
        else:
            pass
        if loopCount > 1:
           time.sleep(3)

    loopCount += 1

conn.close()