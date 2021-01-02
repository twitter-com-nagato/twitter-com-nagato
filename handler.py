#!/usr/bin/env python3

"""
This script has the entry point for the invocation as an AWS Lambda function.
"""

import logging
import microblog.mastodon_api
import microblog.twitter_api
import os
import traceback
from book_search.yahoo_shopping_book_search import YahooShoppingBookSearch
from keyword_extraction.yahoo_keyword_extraction import YahooKeywordExtraction
from nagato import Nagato
from slack_log_handler import SlackLogHandler
from yahoo_api import YahooApi


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
        if slack_webhook_url:
            slack_handler = SlackLogHandler(
                slack_webhook_url, format='%(levelname)s: %(message)s')
            slack_handler.setLevel(logging.WARNING)
            logger.addHandler(slack_handler)

        if os.getenv('NAGATO_LOG_STREAM'):
            stream_handler = logging.StreamHandler()
            logger.addHandler(stream_handler)

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

        yahoo_application_id = os.getenv('YAHOO_APPLICATION_ID')
        assert yahoo_application_id, 'YAHOO_APPLICATION_ID must be a Yahoo! Japan application ID but is not set.'
        yapi = YahooApi(yahoo_application_id)
        book_search = YahooShoppingBookSearch(yapi)
        keyword_extraction = YahooKeywordExtraction(yapi)

        bot = Nagato(api, book_search, keyword_extraction)
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
