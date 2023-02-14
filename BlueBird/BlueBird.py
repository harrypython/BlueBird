import os
from loguru import logger
import tweepy
from dotenv import load_dotenv, find_dotenv


class BlueBird:
    client: tweepy.Client
    expansions: list = ["author_id", "referenced_tweets.id", "referenced_tweets.id.author_id",
                        "entities.mentions.username", "attachments.poll_ids", "attachments.media_keys",
                        "in_reply_to_user_id", "geo.place_id", "edit_history_tweet_ids"],
    media_fields: list = ["alt_text", "duration_ms", "height", "media_key", "preview_image_url", "public_metrics",
                          "type", "url", "variants", "width"],
    place_fields: list = ["contained_within", "country", "country_code", "full_name", "geo", "id", "name",
                          "place_type"],
    poll_fields: list = ["duration_minutes", "end_datetime", "id", "options", "voting_status"],
    tweet_fields: list = ["attachments", "author_id", "context_annotations", "conversation_id", "created_at",
                          "edit_controls", "edit_history_tweet_ids", "entities", "geo", "id", "in_reply_to_user_id",
                          "lang", "possibly_sensitive", "public_metrics", "referenced_tweets", "reply_settings",
                          "source", "text", "withheld"],
    user_fields: list = ["created_at", "description", "entities", "id", "location", "name", "pinned_tweet_id",
                         "profile_image_url", "protected", "public_metrics", "url", "username", "verified",
                         "verified_type", "withheld"]

    def __init__(self):
        """
        The __init__ function is called when an instance of the class is created.
        It initializes attributes that are common to all instances of the class.


        :param self: Reference the current instance of the class
        :return: None
        :doc-author: Trelent
        """
        logger.add("log/file_{time}.log")
        load_dotenv(find_dotenv("config/.env"))
        self.client = tweepy.Client(
            bearer_token=os.getenv("bearer_token"),
            consumer_key=os.getenv("consumer_key"),
            consumer_secret=os.getenv("consumer_secret"),
            access_token=os.getenv("access_token"),
            access_token_secret=os.getenv("access_token_secret")
        )

        return None

    def get_tweet(self, tweet_id: int):
        """
        The get_tweet function retrieves a single tweet from the Twitter API.

        :param self: Access the variables and methods of the class in python
        :param tweet_id:int: Specify the tweet id
        :return: A result object
        :doc-author: Trelent
        """
        try:
            # Get the list of expansions, media fields, and tweet fields
            expansions = list(self.expansions)[0]
            media_fields = list(self.media_fields)[0]
            tweet_fields = list(self.tweet_fields)[0]

            # Make the API call to retrieve the tweet
            result = self.client.get_tweet(
                id=tweet_id,
                user_auth=False,
                expansions=expansions,
                media_fields=media_fields,
                tweet_fields=tweet_fields)

            # Check if the tweet was found
            if hasattr(result, 'data'):
                return result
            else:
                logger.error("Tweet ({}) not found.".format(tweet_id))
                return False
            # Log any exceptions
        except Exception as ex:
            logger.error(ex)

    def get_tweet(self, tweet_id: int):
        """
        The get_tweet function retrieves a tweet from the API using the given tweet ID.

        :param self: Access the class attributes
        :param tweet_id:int: The ID of the tweet to get
        :return: An object, The result of the API call, or False if the tweet was not found
        :doc-author: Trelent
        """
        try:
            # Get the list of expansions, media fields, and tweet fields
            expansions = list(self.expansions)[0]
            media_fields = list(self.media_fields)[0]
            tweet_fields = list(self.tweet_fields)[0]

            # Make the API call to retrieve the tweet
            result = self.client.get_tweet(
                id=tweet_id,
                user_auth=False,
                expansions=expansions,
                media_fields=media_fields,
                tweet_fields=tweet_fields
            )

            # Check if the tweet was found
            if hasattr(result, 'data'):
                return result
            else:
                logger.error("Tweet ({}) not found.".format(tweet_id))
                return False

        # Log any exceptions
        except Exception as ex:
            logger.error(ex)

    def get_tweet_with_replies(self, tweet_id: int):
        """
        The get_tweet_with_replies function accepts a tweet ID and returns the full thread of replies to that tweet.
        The function first searches for the main tweet using its ID, then it uses get_replies to retrieve all replies
        to that specific tweet. The function also sorts the tweets in chronological order (oldest first).


        :param self: Access the class attributes and methods
        :param tweet_id:int: Specify the tweet that we want to get
        :return: A list of tweet objects
        :doc-author: Trelent
        """
        try:
            logger.info("Searching the thread")
            main_tweet = self.get_tweet(tweet_id=tweet_id)
            result = self.get_replies(
                tweet_id=tweet_id,
                tweet_author=str(self.client.get_user(id=main_tweet.data.author_id).data))

            tweets = result.includes['tweets']
            tweets.reverse()
            logger.info("Thread with {} replies founded.".format(len(tweets)))
            return tweets
        except Exception as ex:
            logger.error(ex)

    def duplicate_thread(self, tweet_id: int):
        """
        The duplicate_thread function takes a tweet_id as an argument and returns the URL of the new thread.
        The function first gets all tweets from a given tweet_id, then creates a new thread with those tweets.
        It does this by creating one Tweet at a time, in reply to the previous Tweet.

        :param self: Access the class attributes and methods
        :param tweet_id:int: Pass the id of the tweet that is to be duplicated
        :return: The url of the tweet that was created
        :doc-author: Trelent
        """
        try:
            tweets = self.get_tweet_with_replies(tweet_id=tweet_id)
            in_reply = None
            url_return = None
            for tweet in tweets:
                response = self.client.create_tweet(text=tweet.text, in_reply_to_tweet_id=in_reply)
                if url_return is None:
                    url_return = "https://twitter.com/user/status/{}".format(response.data['id'])
                in_reply = response.data['id']
            logger.success("Your message was posted, check here: {}".format(url_return))
            return url_return
        except Exception as ex:
            logger.error(ex)
