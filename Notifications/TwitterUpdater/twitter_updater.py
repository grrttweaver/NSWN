def classify_alert(alert):

    excluded_severities = ["Minor", "Moderate"]

    twx_alerts = ["Tornado Warning", "Tornado Watch", "Tornado Emergency"]

    ocean_alerts = ["Hurricane Watch", "Hurricane Warning", "Storm Surge Watch", "Storm Surge Warning",
                       "Typhoon Watch", "Typhoon Warning", "Tropical Storm Watch", "Tropical Storm Warning"]

    winter_alerts = ["Blizzard Warning", "Extreme Cold Warning (Alaska only)", "Hard Freeze Warning",
                     "Ice Storm Warning", "Snow Squall Warning", "Winter Storm Watch", "Winter Storm Warning",
                     "Wind Chill Warning", "Avalanche Warning", "Avalanche Watch"]

    reportable_unknown = ["911 Telephone Outage", "Child Abduction Emergency", "Civil Emergency Messages",
                          "Evacuation - Immediate", "Law Enforcement Warning", ""]

    if alert['properties']['severity'] in excluded_severities:
        return "no_tweet"

    elif alert['properties']['event'] in twx_alerts:
        return "Tornado"

    elif alert['properties']['event'] in ocean_alerts:
        return "Ocean"

    elif alert['properties']['event'] in winter_alerts:
        return "Winter"

    elif alert['properties']['event'] in reportable_unknown:
        return "reportable_unknown"

    # By this point, if the alert is classified this high, but not already classified, consider it SWx
    elif alert['properties']['severity'] == "Severe" or "Extreme":
        return "SWx"

    else:
        return "no_tweet"


def main(config, argv, Api):

    swx_twitter = Api(consumer_key=config.get('twitter', 'swx_consumer_key'),
                      consumer_secret=config.get('twitter', 'swx_consumer_secret'),
                      access_token_key=config.get('twitter', 'swx_access_token_key'),
                      access_token_secret=config.get('twitter', 'swx_access_token_secret'),
                      sleep_on_rate_limit=config.get('twitter', 'swx_sleep_on_rate_limit'),
                      tweet_mode=config.get('twitter', 'swx_tweet_mode'))

    twx_twitter = Api(consumer_key=config.get('twitter', 'twx_consumer_key'),
                      consumer_secret=config.get('twitter', 'twx_consumer_secret'),
                      access_token_key=config.get('twitter', 'twx_access_token_key'),
                      access_token_secret=config.get('twitter', 'twx_access_token_secret'),
                      sleep_on_rate_limit=config.get('twitter', 'twx_sleep_on_rate_limit'),
                      tweet_mode=config.get('twitter', 'twx_tweet_mode'))

    frosty_twitter = Api(consumer_key=config.get('twitter', 'frosty_consumer_key'),
                      consumer_secret=config.get('twitter', 'frosty_consumer_secret'),
                      access_token_key=config.get('twitter', 'frosty_access_token_key'),
                      access_token_secret=config.get('twitter', 'frosty_access_token_secret'),
                      sleep_on_rate_limit=config.get('twitter', 'frosty_sleep_on_rate_limit'),
                      tweet_mode=config.get('twitter', 'frosty_tweet_mode'))

    main_twitter = Api(consumer_key=config.get('twitter', 'main_consumer_key'),
                      consumer_secret=config.get('twitter', 'main_consumer_secret'),
                      access_token_key=config.get('twitter', 'main_access_token_key'),
                      access_token_secret=config.get('twitter', 'main_access_token_secret'),
                      sleep_on_rate_limit=config.get('twitter', 'main_sleep_on_rate_limit'),
                      tweet_mode=config.get('twitter', 'main_tweet_mode'))

    ocean_twitter = Api(consumer_key=config.get('twitter', 'ocean_consumer_key'),
                      consumer_secret=config.get('twitter', 'ocean_consumer_secret'),
                      access_token_key=config.get('twitter', 'ocean_access_token_key'),
                      access_token_secret=config.get('twitter', 'ocean_access_token_secret'),
                      sleep_on_rate_limit=config.get('twitter', 'ocean_sleep_on_rate_limit'),
                      tweet_mode=config.get('twitter', 'ocean_tweet_mode'))

    test_twitter = Api(consumer_key=config.get('twitter', 'test_consumer_key'),
                      consumer_secret=config.get('twitter', 'test_consumer_secret'),
                      access_token_key=config.get('twitter', 'test_access_token_key'),
                      access_token_secret=config.get('twitter', 'test_access_token_secret'),
                      sleep_on_rate_limit=config.get('twitter', 'test_sleep_on_rate_limit'),
                      tweet_mode=config.get('twitter', 'test_tweet_mode'))






if __name__ == "__main__":
    from sys import argv
    from configparser import ConfigParser
    from os import path
    from twitter import Api

    config_file = path.abspath(argv[1])
    config_parse = ConfigParser()
    config_parse.read(config_file)

    main(config_parse, argv, Api)
