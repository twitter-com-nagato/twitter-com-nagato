#!/usr/bin/env python3

"""
This script has the entry point for the invocation as an AWS Lambda function.
"""

import logging
import microblog.mastodon_api
import microblog.twitter_api
import nagato
import os
import traceback
from slack_log_handler import SlackLogHandler


def handle(event, context):
    """
    Handles an invocation of AWS Lambda function.
    """

    try:
        logger = logging.getLogger('nagato')
        # Since AWS Lambda may reuse the same function instance,
        # handlers set in the previous execution can be still alive.
        # In order to avoid adding duplicated handlers,
        # clear all the existing handlers beforehand.
        logger.handlers = []
        logger.setLevel(logging.DEBUG)

        slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        assert slack_webhook_url, 'SLACK_WEBHOOK_URL must be a valid Slack webhook URL but is not set.'
        slack_handler = SlackLogHandler(
            slack_webhook_url, format='%(levelname)s: %(message)s')
        slack_handler.setLevel(logging.WARNING)
        logger.addHandler(slack_handler)

        if os.getenv('NAGATO_LOG_STREAM'):
            stream_handler = logging.StreamHandler()
            logger.addHandler(stream_handler)

        yahoo_application_id = os.getenv('YAHOO_APPLICATION_ID')
        assert yahoo_application_id, 'YAHOO_APPLICATION_ID must be a Yahoo! Japan application ID but is not set.'

        twitter_consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
        twitter_consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
        twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        twitter_access_token_secret = os.getenv('TWITTER_ACCESS_SECRET')

        mastodon_access_token = os.getenv('MASTODON_ACCESS_TOKEN')
        mastodon_api_base_url = os.getenv('MASTODON_API_BASE_URL')

        if (twitter_consumer_key and twitter_consumer_secret and twitter_access_token and twitter_access_token_secret):
            api = microblog.twitter_api.TwitterApi(
                    twitter_consumer_key,
                    twitter_consumer_secret,
                    twitter_access_token,
                    twitter_access_token_secret)
        elif (mastodon_access_token and mastodon_api_base_url):
            api = microblog.mastodon_api.MastodonApi(
                    mastodon_access_token,
                    mastodon_api_base_url)
        else:
            raise Exception('All mandatory environment variables are not set.')

        bot = nagato.Nagato(api, yahoo_application_id)
        bot.run()
    except Exception:
        # Catch everything to avoid retrying failed invocations
        # and running multiple instances concurrently.
        if (logger):
            logger.exception('An exception is thrown during running the Nagato bot.')
        else:
            traceback.print_exc()


# Run
if __name__ == '__main__':
    handle(None, None)
