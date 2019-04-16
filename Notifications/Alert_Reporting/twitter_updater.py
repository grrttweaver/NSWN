import twitter

def classify_alert(alert_json):

    excluded_severities = ["Minor", "Moderate"]

    twx_alerts = ["Tornado Warning", "Tornado Watch", "Tornado Emergency"]

    ocean_alerts = ["Hurricane Watch", "Hurricane Warning", "Storm Surge Watch", "Storm Surge Warning",
                    "Typhoon Watch", "Typhoon Warning", "Tropical Storm Watch", "Tropical Storm Warning"]

    winter_alerts = ["Blizzard Warning", "Extreme Cold Warning (Alaska only)", "Hard Freeze Warning",
                     "Ice Storm Warning", "Snow Squall Warning", "Winter Storm Watch", "Winter Storm Warning",
                     "Wind Chill Warning", "Avalanche Warning", "Avalanche Watch"]

    reportable_unknown = ["911 Telephone Outage", "Child Abduction Emergency", "Civil Emergency Messages",
                          "Evacuation - Immediate", "Law Enforcement Warning", ""]

    if alert_json['properties']['severity'] in excluded_severities:
        return "no_tweet"

    elif alert_json['properties']['event'] in twx_alerts:
        return "Tornado"

    elif alert_json['properties']['event'] in ocean_alerts:
        return "Ocean"

    elif alert_json['properties']['event'] in winter_alerts:
        return "Winter"

    elif alert_json['properties']['event'] in reportable_unknown:
        return "reportable_unknown"

    # By this point, if the alert is classified this high, but not already classified, consider it SWx
    elif alert_json['properties']['severity'] == "Severe" or "Extreme":
        return "SWx"

    else:
        return "no_tweet"


def make_tweet_text(alert_json):
    alert_json = alert_json['properties']
    tweet = "The {} Office has issued a {} for {}. Expiring at {}".format(alert_json['senderName'], alert_json['event'],
                                                                          alert_json['areaDesc'], alert_json['expires'])

    if tweet.__len__() > 140:
        tweet = "{}...".format(tweet[:137])

    return tweet


def main(config, alert):

    swx_twitter = twitter.Api(consumer_key=config.get('twitter', 'swx_consumer_key'),
                              consumer_secret=config.get('twitter', 'swx_consumer_secret'),
                              access_token_key=config.get('twitter', 'swx_access_token_key'),
                              access_token_secret=config.get('twitter', 'swx_access_token_secret'),
                              sleep_on_rate_limit=config.get('twitter', 'swx_sleep_on_rate_limit'),
                              tweet_mode=config.get('twitter', 'swx_tweet_mode'))

    twx_twitter = twitter.Api(consumer_key=config.get('twitter', 'twx_consumer_key'),
                              consumer_secret=config.get('twitter', 'twx_consumer_secret'),
                              access_token_key=config.get('twitter', 'twx_access_token_key'),
                              access_token_secret=config.get('twitter', 'twx_access_token_secret'),
                              sleep_on_rate_limit=config.get('twitter', 'twx_sleep_on_rate_limit'),
                              tweet_mode=config.get('twitter', 'twx_tweet_mode'))

    frosty_twitter = twitter.Api(consumer_key=config.get('twitter', 'frosty_consumer_key'),
                                 consumer_secret=config.get('twitter', 'frosty_consumer_secret'),
                                 access_token_key=config.get('twitter', 'frosty_access_token_key'),
                                 access_token_secret=config.get('twitter', 'frosty_access_token_secret'),
                                 sleep_on_rate_limit=config.get('twitter', 'frosty_sleep_on_rate_limit'),
                                 tweet_mode=config.get('twitter', 'frosty_tweet_mode'))

    main_twitter = twitter.Api(consumer_key=config.get('twitter', 'main_consumer_key'),
                               consumer_secret=config.get('twitter', 'main_consumer_secret'),
                               access_token_key=config.get('twitter', 'main_access_token_key'),
                               access_token_secret=config.get('twitter', 'main_access_token_secret'),
                               sleep_on_rate_limit=config.get('twitter', 'main_sleep_on_rate_limit'),
                               tweet_mode=config.get('twitter', 'main_tweet_mode'))

    ocean_twitter = twitter.Api(consumer_key=config.get('twitter', 'ocean_consumer_key'),
                                consumer_secret=config.get('twitter', 'ocean_consumer_secret'),
                                access_token_key=config.get('twitter', 'ocean_access_token_key'),
                                access_token_secret=config.get('twitter', 'ocean_access_token_secret'),
                                sleep_on_rate_limit=config.get('twitter', 'ocean_sleep_on_rate_limit'),
                                tweet_mode=config.get('twitter', 'ocean_tweet_mode'))

    test_twitter = twitter.Api(consumer_key=config.get('twitter', 'test_consumer_key'),
                               consumer_secret=config.get('twitter', 'test_consumer_secret'),
                               access_token_key=config.get('twitter', 'test_access_token_key'),
                               access_token_secret=config.get('twitter', 'test_access_token_secret'),
                               sleep_on_rate_limit=config.get('twitter', 'test_sleep_on_rate_limit'),
                               tweet_mode=config.get('twitter', 'test_tweet_mode'))

    alert_class = classify_alert(alert)

    if alert_class == "Tornado":
        tweet = make_tweet_text(alert)
        twx_twitter.PostUpdate(tweet)
        swx_twitter.PostUpdate(tweet)

    elif alert_class == "Ocean":
        tweet = make_tweet_text(alert)
        ocean_twitter.PostUpdate(tweet)
        swx_twitter.PostUpdate(tweet)

    elif alert_class == "Winter":
        tweet = make_tweet_text(alert)
        frosty_twitter.PostUpdate(tweet)
        swx_twitter.PostUpdate(tweet)

    elif alert_class == "SWx":
        tweet = make_tweet_text(alert)
        swx_twitter.PostUpdate(tweet)

    elif alert_class == "reportable_unknown":
        tweet = make_tweet_text(alert)
        main_twitter.PostUpdate(tweet)

    elif alert_class == "no_tweet":
        pass

    else:
        tweet = make_tweet_text(alert)
        print("{} - Didn't get tweeted / properly classified!".format(tweet))