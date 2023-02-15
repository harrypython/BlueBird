import os
import datetime

from loguru import logger
import tweepy
from dotenv import load_dotenv, find_dotenv


def shorten_tweet(string_text: str, limit: int = 280):
    """
    The shorten_tweet function takes a string and shortens it to 280 characters.
    If the length of the string is already less than or equal to 280, return the original string.
    Otherwise, extract the final link from the string if any and remove it from
    the remaining text before adding words back together until reaching 280 characters.

    :param string_text:str: Pass the text of the tweet
    :param limit:int=280: Specify the maximum length of a tweet
    :return: The string_text parameter if the length of
    :doc-author: Trelent
    """
    # If the length of the string is already less than or equal to the limit,
    # return the original string
    if len(string_text) <= limit:
        return string_text

    # Extract the final link from the string, if any
    link_final = "https://" + string_text.split("https://")[-1]

    # Remove the final link from the string and strip any leading/trailing spaces
    string_text = string_text.split(link_final)[0].strip()

    # Calculate the remaining length of the string after adding the final link
    length = limit - len(link_final) - 1  # subtract 1 to account for the space

    # Split the remaining text into words and add words to the result
    # until the length limit is reached
    while len(string_text) > length:
        words = string_text.split(" ")
        string_text = " ".join(words[:-1]).strip()

    # Remove trailing space, if any, and add the final link to the result
    return string_text.strip() + " " + link_final


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

    def get_replies(self, tweet: tweepy.client.Response):
        """
        The get_replies function retrieves the replies to a tweet.

        :param self: Access the class attributes and methods
        :param tweet:tweepy.client.Response: Pass the tweet object to the function
        :return: A response object
        :doc-author: Trelent
        """
        try:
            # Get the author of the tweet as a string
            tweet_author = str(self.client.get_user(id=tweet.data.author_id).data)

            # Extract the first element of each query parameter list
            expansions = list(self.expansions)[0]
            media_fields = list(self.media_fields)[0]
            tweet_fields = list(self.tweet_fields)[0]
            place_fields = list(self.place_fields)[0]
            poll_fields = list(self.poll_fields)[0]
            user_fields = list(self.user_fields)[0]

            # Construct the query string for the Twitter API search
            str_query = "(url:{} from:{}) OR ( conversation_id:{} from:{})".format(
                tweet.data.conversation_id, tweet_author, tweet.data.conversation_id, tweet_author)

            # Execute the Twitter API search
            result = self.client.search_recent_tweets(
                query=str_query,
                expansions=expansions,
                media_fields=media_fields,
                tweet_fields=tweet_fields,
                place_fields=place_fields,
                poll_fields=poll_fields,
                user_fields=user_fields
            )

            # Check if the search returned any results
            if hasattr(result, 'data'):
                return result
            else:
                # Log an error message and return False if no results were found
                logger.error("Tweet replies ({}) not found.".format(tweet.data.conversation_id))
                return False
        except Exception as ex:
            # Log any exceptions that occurred during the method execution
            logger.error(ex)

    def get_tweet_with_replies(self, tweet_id: int):
        """
        The get_tweet_with_replies function takes a tweet ID as an argument and returns a list of
        dictionaries containing the text of the tweets in the thread, along with any media attached to them.
        The function will return an empty list if no replies are found or if there is more than 7 days between
        the original tweet and now.

        :param self: Reference the class instance
        :param tweet_id:int: Specify the tweet id of the main tweet
        :return: A list of dictionaries where each dictionary contains the tweet id and its text
        :doc-author: Trelent
        """
        try:
            # Log that we are starting the thread search
            logger.info("Searching the thread")

            # Get the main tweet of the thread
            main_tweet = self.get_tweet(tweet_id=tweet_id)

            # Check if the tweet is more than 7 days old
            if (datetime.datetime.now().replace(tzinfo=None) - main_tweet.data.created_at.replace(
                    tzinfo=None)).days > 7:
                logger.error("This tweet has more than 7 days.")
                quit()

            # Get the replies to the main tweet
            result = self.get_replies(tweet=main_tweet)

            # Process the replies and store them in a list of dictionaries
            tweets = []
            for tweet in [item for item in result.includes['tweets'] if not item.text.startswith("RT")]:
                tweets.append(
                    {
                        tweet.id: dict(
                            text=tweet.text,
                            attachments=(None if tweet.attachments is None else tweet.attachments['media_keys'])
                        )
                    }
                )

            # Sort the list of replies by tweet ID
            tweets = sorted(tweets, key=lambda x: list(x.keys())[0])

            # Log the number of replies found
            logger.info("Thread with {} replies founded.".format(len(tweets)))

            # Return the list of replies
            return tweets
        except Exception as ex:
            # Log any exceptions that occur
            logger.error(ex)

    def duplicate_thread(self, tweet_id: int):
        """
        The duplicate_thread function takes a tweet_id as an argument and creates a thread of tweets in reply to
        the given tweet_id. The function returns the URL of the first tweet created in the thread.

        :param self: Access the class attributes and methods
        :param tweet_id:int: Pass the tweet_id of the tweet that is to be replied to
        :return: A url to the first tweet that was created in the thread
        :doc-author: Trelent
        """
        try:
            tweets = self.get_tweet_with_replies(tweet_id=tweet_id)  # get tweets in thread with given tweet_id
            in_reply = None  # initialize the in_reply variable to None
            url_return = None  # initialize the url_return variable to None
            for tweet in tweets:
                # shorten the tweet text to fit the character limit
                tweet_text = shorten_tweet(list(tweet.values())[0]['text'])
                # create a tweet in reply to the previous tweet in the thread
                response = self.client.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=in_reply
                )
                # if url_return is None, set it to the URL of the first tweet created in the thread
                if url_return is None:
                    url_return = "https://twitter.com/user/status/{}".format(response.data['id'])
                # set the in_reply variable to the ID of the tweet that was just created
                in_reply = response.data['id']
            logger.success("Your message was posted, check here: {}".format(url_return))
            return url_return
        except Exception as ex:
            logger.error(ex)
