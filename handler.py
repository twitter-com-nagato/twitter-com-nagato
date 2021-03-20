#!/usr/bin/env python3

"""
This script has the entry point for the invocation as an AWS Lambda function.
"""

import logging
import os
import sys
import traceback
from book_search import yahoo_shopping_book_search
from keyword_extraction import yahoo_keyword_extraction
from microblog import mastodon_api
from microblog import twitter_api
from nagato import Nagato
from slack_log_handler import SlackLogHandler
from yahoo_api import YahooApi


def setup_logger(nagato):
    logger = nagato.getLogger()
    logger.setLevel(logging.DEBUG)

    # Add a Slack logger
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if slack_webhook_url:
        slack_handler = SlackLogHandler(
            slack_webhook_url, format='%(levelname)s: %(message)s')
        slack_handler.setLevel(logging.WARNING)
        logger.addHandler(slack_handler)

    # Add a console logger
    if os.getenv('NAGATO_LOG_STREAM'):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)


def create_twitter_api():
    twitter_consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
    twitter_consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
    twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    twitter_access_token_secret = os.getenv('TWITTER_ACCESS_SECRET')
    assert twitter_consumer_key
    assert twitter_consumer_secret
    assert twitter_access_token
    assert twitter_access_token_secret
    return twitter_api.TwitterApi(
            twitter_consumer_key,
            twitter_consumer_secret,
            twitter_access_token,
            twitter_access_token_secret)


def create_mastodon_api():
    mastodon_access_token = os.getenv('MASTODON_ACCESS_TOKEN')
    mastodon_api_base_url = os.getenv('MASTODON_API_BASE_URL')
    assert mastodon_access_token
    assert mastodon_api_base_url
    return mastodon_api.MastodonApi(
            mastodon_access_token,
            mastodon_api_base_url)


def create_yahoo_api():
    yahoo_application_id = os.getenv('YAHOO_APPLICATION_ID')
    assert yahoo_application_id
    return YahooApi(yahoo_application_id)


def create_microblog_api():
    if os.getenv('MASTODON_API_BASE_URL'):
        return create_mastodon_api()
    else:
        return create_twitter_api()


def create_nagato():
    mapi = create_microblog_api()
    yapi = create_yahoo_api()
    book_search = yahoo_shopping_book_search.YahooShoppingBookSearch(yapi)
    keyword_extraction = yahoo_keyword_extraction.YahooKeywordExtraction(yapi)
    nagato = Nagato(mapi, book_search, keyword_extraction)
    setup_logger(nagato)
    return nagato


def post(event, context):
    nagato = create_nagato()
    nagato.postRandomPhrase()


def refollow(event, context):
    nagato = create_nagato()
    nagato.refollow()


def reply(event, context):
    nagato = create_nagato()
    nagato.respondNewReply()


def run(event, context):
    nagato = create_nagato()
    nagato.run()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        run(None, None)
    else:
        operation = sys.argv[1]
        if operation == 'post':
            post(None, None)
        elif operation == 'refollow':
            refollow(None, None)
        elif operation == 'reply':
            reply(None, None)
        else:
            raise Exception('Unsupported operation: %s' % operation)
