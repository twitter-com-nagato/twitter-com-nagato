#!/usr/bin/env python3

"""
This is a module to operate Nagato bot.
"""

import datetime
import logging
import os
import pytz
import random
import re
import urllib
import yahoo


def ara2kan(ara):
    """
    Converts the specified number to the Kanji number text.
    """

    assert ara >= 0 and ara < 100
    kan = '零一二三四五六七八九十'
    return '%s%s%s' % (
        kan[int(ara / 10)] if ara >= 20 else '',
        '十' if ara >= 10 else '',
        kan[ara % 10] if ara < 10 or ara % 10 else ''
    )


def get_greeting():
    """
    Gets the greeting text based on the current time.
    """

    # Get the current time in JST
    now = datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo'))
    status = '%s時%s分。' % (ara2kan(now.hour), ara2kan(now.minute))

    # Additional messages probability is 20%
    if random.randrange(5):
        if 5 <= now.hour < 10:
            status += 'おはよう。'
        elif 10 <= now.hour < 18:
            status += 'こんにちは。'
        elif 18 <= now.hour < 23:
            status += 'こんばんは。'
        else:
            status += 'おやすみなさい。'
    else:
        # Additional messages
        if 5 <= now.hour < 9:
            status += '早起きは三文の得。'
        elif 9 <= now.hour < 11:
            status += 'そろそろおでかけ。'
        elif 11 <= now.hour < 13:
            status += '昼食の時間。'
        elif 13 <= now.hour < 16:
            status += '三時のおやつ、忘れずに。'
        elif 16 <= now.hour < 19:
            status += 'お疲れ様。'
        elif 19 <= now.hour < 23:
            status += '明日も頑張って。'
        else:
            status += '良い子は寝る時間。'
    return status


def is_book_recommendation_request(text):
    """
    Returns true if the specified text requests a book recommendation.
    """

    book_re = '((お|御|オ)(勧|薦|すす|奨|スス)(め|メ)の|(面白|オモシロ|おもしろ)(い|イ))(図書|本|書籍|書物)'
    return not re.search(book_re, text) is None


def is_greeting_request(text):
    """
    Returns true if the specified text is a greeting.
    """

    greeting_re = '(お(はよ|やすみ)|(こん(にち|ばん)[は|わ]))'
    return not re.search(greeting_re, text) is None


def is_timeline_speed_request(text):
    """
    Returns true if the specified text requests the home timeline speed.
    """

    tlspeed_re = '流速'
    return not re.search(tlspeed_re, text) is None


def is_url(text):
    """
    Returns True if the specified text is a valid URL.
    """

    try:
        return bool(urllib.parse.urlparse(text).scheme)
    except Exception:
        return False


def get_random_phrase():
    """
    Gets a random phrase from the phrase text file.
    """

    phrase_file = os.path.join(os.path.dirname(__file__), 'phrases.txt')
    with open(phrase_file, mode='r', encoding='utf-8') as phrase_text:
        return random.choice(phrase_text.readlines()).strip()


class Nagato(object):
    """
    A class for Nagato bot.
    """

    def __init__(
        self,
        microblog,
        yahoo_application_id
    ):

        assert microblog, 'A microblog service should be specified.'
        assert yahoo_application_id, 'Yahoo! Japan application ID is mandatory but not set.'

        # Add a null handler to suppress standard error outputs
        # even when there is no additional handler.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        self.yapi = yahoo.Yahoo(yahoo_application_id)
        self.microblog = microblog
        self.tlspeed = 0

    def get_timeline_speed(self):
        """
        Outputs the home timeline speed to the log.
        """

        if not self.tlspeed:
            statuses = self.microblog.get_home_statuses()
            timestamps = [status.created_at for status in statuses]
            spent = max((max(timestamps) - min(timestamps)).total_seconds(), 1)
            self.tlspeed = len(statuses) * 3600 / spent
        return self.tlspeed

    def get_key_phrase(self, user_id):
        """
        Gets words from the user timeline except @replies and URIs
        and extracts key phrases from them using Yahoo! Japan API.
        """

        statuses = self.microblog.get_user_statuses(user_id)
        texts = ' '.join([status.text for status in statuses])
        # Remove all HTML elements assuming that '>' in attributes or contents is always escaped.
        texts = re.sub(r'<[^>]*>', '', texts)
        words = [word for word in re.split(r'\s', texts)
                 if word and (word[0] != '@') and (not is_url(word))]
        texts = ' '.join(words)
        self.logger.debug('Words in statuses of #%d: %s', user_id, texts)

        # Access to Yahoo! API
        return self.yapi.get_key_phrase(texts)

    def recommend(self, key_phrases):
        """
        Recommends a book based on the specified key phrases
        using Yahoo! Japan item search API.
        """

        self.logger.debug('Start a recommendation with keyphrases: %s', key_phrases)
        cand = None
        canl = 0
        indexes = [0]
        while True:
            # Query
            self.logger.debug('Indice: %s', indexes)
            queries = [key_phrases[i] for i in indexes]
            (item, total) = self.yapi.search_item(
                queries, {'category_id': 10002, 'hits': 1})
            self.logger.debug('%s -> %s (%d)', queries, item, total)

            # Update the best result set
            if total > 0 and (not cand or total < canl):
                self.logger.debug('Candidate: %s -> %s', cand, item[0])
                canl = total
                cand = item[0]

            if total == 0:
                # Not found
                if indexes[-1] < len(key_phrases) - 1:
                    # Go ahead
                    indexes[-1] += 1
                elif len(indexes) > 1:
                    # Go up
                    indexes = indexes[:-1]
                    if indexes[-1] < len(key_phrases) - 1:
                        indexes[-1] += 1
                    else:
                        break
                else:
                    # No way
                    break
            elif total == 1:
                # Only one
                break
            else:
                # Many
                if indexes[-1] < len(key_phrases) - 1:
                    # More keywords
                    indexes += [indexes[-1] + 1]
                else:
                    # No way
                    break

        if cand:
            title = cand['Name']
            url = cand['Url']
            self.logger.info('Recommend: %s %s', title, url)
            return (title, url)

        self.logger.warning('Recommend: Not Found for %s', key_phrases)
        return ('分からない', None)

    def get_last_replied_status_id(self, my_statuses=None):
        """
        Gets the maximum ID of statuses which this account sent a reply to.
        """

        if my_statuses == None:
            my_statuses = self.microblog.get_user_statuses(self.credential.id)

        if not my_statuses:
            self.logger.debug(
                '@%s hasn\'t sent any status yet.',
                self.credential.screen_name)
            return 0

        my_last_status = my_statuses[0]
        if my_last_status.in_reply_to_status_id:
            self.logger.debug(
                '@%s replied to #%d most recently.',
                self.credential.screen_name,
                my_last_status.in_reply_to_status_id)
            return my_last_status.in_reply_to_status_id
        else:
            self.logger.debug(
                '@%s sent status #%d most recently.',
                self.credential.screen_name,
                my_last_status.id)
            return my_last_status.id

    def get_last_sent_message_id(self):
        """
        Gets the maximum ID of messages sent from this account.
        """

        sent_message_ids = [sent_message.id for sent_message in self.microblog.get_sent_messages()]
        last_sent_message_id = max(sent_message_ids) if sent_message_ids else 0
        self.logger.debug('The last message ID is #%d.', last_sent_message_id)
        return last_sent_message_id

    def get_new_message(self):
        """
        Gets a new message which this account hasn't responded yet.
        """

        last_sent_message_id = self.get_last_sent_message_id()
        messages = self.microblog.get_received_messages(last_sent_message_id + 1)
        for message in messages:
            assert message.id > last_sent_message_id
            assert message.user.id != self.credential.user.id
            self.logger.info(
                'Found a new message (#%d) @%s: %s...',
                message.id,
                message.user.id,
                message.text[64])
            return message

        return None

    def get_new_reply(self):
        """
        Gets a new reply which this account hasn't responded yet.
        """

        max_replied_status_id = self.get_last_replied_status_id()
        replies = self.microblog.get_replies(max_replied_status_id + 1)
        self.logger.debug(
            'Received %d new replies since #%d.',
            len(replies),
            (max_replied_status_id + 1))

        for reply in replies:
            if reply.id > max_replied_status_id:
                assert reply.user.id != self.credential.id
                self.logger.debug(
                    'Found a new reply (#%d) @%s#%d: %s',
                    reply.id,
                    reply.user.screen_name,
                    reply.user.id,
                    reply.text)
                return reply

        return None

    def refollow(self):
        """
        Follows new followers and removes ex-followers.
        """

        friend_ids = self.microblog.get_friend_ids()
        self.logger.debug('Retrieved %d friends.', len(friend_ids))

        follower_ids = self.microblog.get_follower_ids()
        self.logger.debug('Retrieved %d followers.', len(follower_ids))

        outgoing_ids = self.microblog.get_pending_friend_ids()
        self.logger.debug(
            'Retrieved %d protected users with pending follow requests.',
            len(outgoing_ids))

        for friend_id in friend_ids - follower_ids:
            self.logger.info('Removing #%d', friend_id)
            self.microblog.remove(friend_id)

        for follower_id in follower_ids - friend_ids - outgoing_ids:
            self.logger.info('Following #%d', follower_id)
            self.microblog.follow(follower_id)

    def get_response(self, user_id, text):
        """
        Returns the status text and URL to respond to the specified text.
        """

        status = None
        url = None

        if is_book_recommendation_request(text):
            key_phrases = self.get_key_phrase(user_id)
            (status, url) = self.recommend(key_phrases[:10])
        elif is_greeting_request(text):
            status = get_greeting()
        elif is_timeline_speed_request(text):
            status = '流速 %d' % self.get_timeline_speed()
        else:
            status = get_random_phrase()

        return (status, url)

    def respond_reply(self, reply):
        """
        Reply to the specified incoming reply.
        """

        (text, url) = self.get_response(reply.user.id, reply.text)
        self.microblog.post(text, url, reply)
        self.logger.info(
            'Sent a reply to @%s: %s',
            reply.user.screen_name, text)

    def respond_message(self, message):
        """
        Send a response to the specified message.
        """

        # Block-then-unblock anyone who sends a message with URIs
        # in order to avoid re-following again.
        words = re.split(r'\s', message.text)
        urls = [is_url(word) for word in words]
        if urls:
            text = 'YUKI.N>パーソナルネーム%sを敵性と判定。当該対象の有機情報連結を解除する。' % message.sender_screen_name
            self.microblog.send(text, message.user.id)
            self.microblog.delete_message(message.id)
            self.microblog.block(message.user.id)
            self.microblog.unblock(message.user.id)
            self.logger.info(
                'Destroyed the message from and friendship with #%d.',
                message.user.id)
            return

        (status, url) = self.get_response(message.user.id, message.text)
        text = (status + ' ' + url) if url else status
        self.microblog.send(text, message.user.id)
        self.logger.info('Sent a response message to @%s: %s',
                         message.sender_screen_name, text)

    def post_random_phrase(self):
        phrase = get_random_phrase()
        self.microblog.post(phrase)

    def run(self):
        """
        Executes the bot.
        """

        self.logger.debug('Executing...')
        self.credential = self.microblog.verify_credentials()

        reply = self.get_new_reply()
        if reply:
            self.respond_reply(reply)

        message = self.get_new_message()
        if message:
            self.respond_message(message)

        # Post randomly roughly once a day.
        if not random.randrange(60 * 24):
            self.post_random_phrase()

        self.refollow()

        self.logger.info('The home timeline speed is %d statuses/s', self.get_timeline_speed())
        self.logger.debug('Terminating...')

# vim:set fenc=utf-8 ts=4 sw=4:
