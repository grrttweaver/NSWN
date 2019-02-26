from datetime import datetime
import json, requests, time, twitter, configparser, os

HERE = os.path.abspath(os.path.dirname(__file__))
configFilePath = os.path.join(HERE, '../NSWN_Config.ini')
config = configparser.ConfigParser()
config.read(configFilePath)


def logToFile(line):
    log_file = open("Twitter.log", "a+")
    log_file.write(line)
    log_file.write("\n")
    log_file.close()


url = config.get("noaa", "api_url")

SevereAlerts = twitter.Api(consumer_key=config.get('twitter', 'swx_consumer_key'),
                           consumer_secret=config.get('twitter', 'swx_consumer_secret'),
                           access_token_key=config.get('twitter', 'swx_access_token_key'),
                           access_token_secret=config.get('twitter', 'swx_access_token_secret'),
                           sleep_on_rate_limit=config.get('twitter', 'swx_sleep_on_rate_limit'),
                           tweet_mode=config.get('twitter', 'swx_tweet_mode'))


TornadoAlerts = twitter.Api(consumer_key=config.get('twitter', 'twx_consumer_key'),
                            consumer_secret=config.get('twitter', 'twx_consumer_secret'),
                            access_token_key=config.get('twitter', 'twx_access_token_key'),
                            access_token_secret=config.get('twitter', 'twx_access_token_secret'),
                            sleep_on_rate_limit=config.get('twitter', 'twx_sleep_on_rate_limit'),
                            tweet_mode=config.get('twitter', 'twx_tweet_mode'))

while True:
    resp = requests.get(url)
    tweets = SevereAlerts.GetUserTimeline(config['twitter']['swx_timeline'])

    didTweet = False

    if resp == 200:
        logToFile(resp.status_code)
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
            if item['messageType'] == 'Alert' \
                    and item['severity'] != "Minor" \
                    and item['severity'] != "Moderate" \
                    and item['severity'] != "Unknown" \
                    and item['event'] != "Red Flag Warning" \
                    and item['event'] != "Fire Weather Watch" \
                    and item['event'] != "Special Marine Warning" \
                    and item['event'] != "Flood Warning" \
                    and item['event'] != "Flood Watch" \
                    and item['event'] != "Flash Flood Watch" \
                    and item['event'] != "High Wind Warning" \
                    and item['event'] != "Severe Thunderstorm Watch" \
                    and item['event'] != "Excessive Heat Watch" \
                    and item['event'] != "Excessive Heat Warning" \
                    and item['event'] != "Blizzard Warning" \
                    and item['event'] != "Snow Squall Warning" \
                    and item['event'] != "Flash Flood Warning":
                severeAlerts.append(item)

        for alert in severeAlerts:
            office = alert['senderName']
            event = alert['event']
            area = alert['areaDesc']
            expires = alert['expires']
            severity = alert['severity']
            status = "A {} has been issued for {}.  Expiring at: {} ".format(event, area, expires)
            print(status)

            found = False
            for tweet in tweets:
                tweetCheck = str(tweet.full_text).replace(" ","")
                statusNoSpace = status.replace(" ","")
                if tweetCheck == statusNoSpace:
                    found = True
                if tweetCheck == status:
                    found = True

            if not found:
                try:
                    if len(status) <= 140:
                        maybeTweet = "The {} Office has issued a {} for {}. Expiring at {}".format(office,event,area,expires)
                        if len(maybeTweet) <= 140:
                            if str(severity) == "Extreme":
                                tweet = TornadoAlerts.PostUpdate(maybeTweet)
                            else:
                                tweet = SevereAlerts.PostUpdate(maybeTweet)

                        else:
                            if str(severity) == "Extreme":
                                tweet = TornadoAlerts.PostUpdate(status)
                            else:
                                tweet = SevereAlerts.PostUpdate(status)
                    else:
                        if str(severity) == "Extreme":
                            tweet = TornadoAlerts.PostUpdate("{}...".format(status[:137]))
                        else:
                            tweet = SevereAlerts.PostUpdate("{}...".format(status[:137]))

                    logToFile(tweet.text)
                    didTweet = True
                    time.sleep(5)
                except Exception as err:
                    errMessage = dict(err.message[0])
                    errMess = errMessage['message']
                    if errMess == "Status is a duplicate.":
                        pass
                    else:
                        logToFile("***\t\t{} \n\t Problem with tweeting: {}".format(status, errMess))
            else:
                pass
            found = False
    if didTweet:
        pass
    else:
        logToFile("Nothing new. Checked at {}".format(str(datetime.now())))
        print("Nothing new. Checked at {}".format(str(datetime.now())))
    time.sleep(60)