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

    def __init__(self, microblog, book_search, keyword_extraction):

        assert microblog
        assert book_search
        assert keyword_extraction

        self.logger = self.getLogger()
        # Since AWS Lambda may reuse the same function instance,
        # handlers set in the previous execution can be still alive.
        # In order to avoid adding duplicated handlers,
        # clear all the existing handlers beforehand.
        self.logger.handlers = []
        # Add a null handler to suppress standard error outputs
        # even when there is no additional handler.
        self.logger.addHandler(logging.NullHandler())
        self.book_search = book_search
        self.keyword_extraction = keyword_extraction
        self.microblog = microblog
        self.tlspeed = 0

    def getLogger(self):
        return logging.getLogger(__name__)

    def getTimelineSpeed(self):
        """
        Gets the number of statues in the home timeline per second.
        """

        if not self.tlspeed:
            statuses = self.microblog.get_home_statuses()
            timestamps = [status.created_at for status in statuses]
            spent = max((max(timestamps) - min(timestamps)).total_seconds(), 1)
            self.tlspeed = len(statuses) * 3600 / spent
        return self.tlspeed

    def getUserKeyPhrases(self, user_id):
        """
        Gets words from the user timeline except @replies and URIs
        and extracts key phrases from them using a keyword extractor.
        """

        statuses = self.microblog.get_user_statuses(user_id)
        texts = ' '.join([status.text for status in statuses])
        # Remove all HTML elements assuming that '>' in attributes or contents is always escaped.
        texts = re.sub(r'<[^>]*>', '', texts)
        words = [word for word in re.split(r'\s', texts)
                 if word and (word[0] != '@') and (not is_url(word))]
        texts = ' '.join(words)
        self.logger.debug('Words in statuses of #%d: %s', user_id, texts)

        return self.keyword_extraction.extract(texts)

    def recommendBook(self, key_phrases):
        """
        Recommends a book based on the specified key phrases using an item search API.
        """

        self.logger.debug('Start a book recommendation with key phrases: %s', key_phrases)
        best_book = None
        best_result_count = 0
        key_phrase_indice = [0]
        while True:
            # Query
            self.logger.debug('Key phrase indice: %s', key_phrase_indice)
            queries = [key_phrases[i] for i in key_phrase_indice]
            (top_book, result_count) = self.book_search.search(queries)
            self.logger.debug('%s -> %s (%d)', queries, top_book, result_count)

            # Update the best result set
            if top_book and ((not best_book) or (result_count < best_result_count)):
                self.logger.debug('Candidate: %s -> %s', best_book, top_book)
                best_result_count = result_count
                best_book = top_book

            if result_count == 0:
                # Not found
                if key_phrase_indice[-1] < len(key_phrases) - 1:
                    # Go ahead
                    key_phrase_indice[-1] += 1
                elif len(key_phrase_indice) > 1:
                    # Go up
                    key_phrase_indice = key_phrase_indice[:-1]
                    if key_phrase_indice[-1] < len(key_phrases) - 1:
                        key_phrase_indice[-1] += 1
                    else:
                        break
                else:
                    # No way
                    break
            elif result_count == 1:
                # Only one
                break
            else:
                # Many
                if key_phrase_indice[-1] < len(key_phrases) - 1:
                    # More keywords
                    key_phrase_indice += [key_phrase_indice[-1] + 1]
                else:
                    # No way
                    break

        self.logger.info('Recommend: %s', best_book)
        return best_book

    def getLastRepliedStatusId(self, my_statuses=None):
        """
        Gets the maximum ID of statuses which this account sent a reply to.
        """

        if my_statuses is None:
            my_statuses = self.microblog.get_user_statuses(self.credential.id)

        if my_statuses is None:
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

    def getLastSentMessageId(self):
        """
        Gets the maximum ID of messages sent from this account.
        """

        sent_message_ids = [sent_message.id for sent_message in self.microblog.get_sent_messages()]
        last_sent_message_id = max(sent_message_ids) if sent_message_ids else 0
        self.logger.debug('The last message ID is #%d.', last_sent_message_id)
        return last_sent_message_id

    def getNewMessage(self):
        """
        Gets a new message which this account hasn't responded yet.
        """

        last_sent_message_id = self.getLastSentMessageId()
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

    def getNewReply(self):
        """
        Gets a new reply which this account hasn't responded yet.
        """

        max_replied_status_id = self.getLastRepliedStatusId()
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

    def getBookRecommendation(self, user_id):
        key_phrases = self.getUserKeyPhrases(user_id)
        self.logger.info('Book Recommendation Keyphrases: %s', key_phrases)
        book = self.recommendBook(key_phrases[:10])
        self.logger.info('Book Recommendation: %s', book)
        if book:
            return (book.name, book.url)
        else:
            return ('分からない', None)

    def getResponse(self, user_id, text):
        """
        Returns the status text and URL to respond to the specified text.
        """

        status = None

        if is_book_recommendation_request(text):
            return self.getBookRecommendation(user_id)
        elif is_greeting_request(text):
            status = get_greeting()
        elif is_timeline_speed_request(text):
            status = '流速 %d' % self.getTimelineSpeed()
        else:
            status = get_random_phrase()

        return (status, None)

    def respondReply(self, reply):
        """
        Reply to the specified incoming reply.
        """

        (text, url) = self.getResponse(reply.user.id, reply.text)
        self.microblog.post(text, url, reply)
        self.logger.info(
            'Sent a reply to @%s: %s',
            reply.user.screen_name, text)

    def respondMessage(self, message):
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

        (status, url) = self.getResponse(message.user.id, message.text)
        text = (status + ' ' + url) if url else status
        self.microblog.send(text, message.user.id)
        self.logger.info('Sent a response message to @%s: %s',
                         message.sender_screen_name, text)

    def postRandomPhrase(self):
        phrase = get_random_phrase()
        self.microblog.post(phrase)

    def run(self):
        """
        Executes the bot.
        """

        self.logger.debug('Executing...')
        self.credential = self.microblog.verify_credentials()

        reply = self.getNewReply()
        if reply:
            self.respondReply(reply)

        message = self.getNewMessage()
        if message:
            self.respondMessage(message)

        # Post randomly roughly once a day.
        if not random.randrange(60 * 24):
            self.postRandomPhrase()

        self.logger.info('The home timeline speed is %d statuses/s', self.getTimelineSpeed())
        self.logger.debug('Terminating...')

# vim:set fenc=utf-8 ts=4 sw=4:
