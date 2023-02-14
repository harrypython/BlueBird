import argparse
from BlueBird import BlueBird

"""Duplicate a thread from Twitter using the BlueBird library.
 Parameters:
 thread (str): The URL of the first tweet from the thread you want to duplicate
 Returns:
 None
"""
# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-t", "--thread", help="First tweet from the thread you want to duplicate (repost)")

# Read arguments from command line
args = parser.parse_args()

# If the thread argument is in the form of a Twitter URL, extract the tweet ID
if "twitter" in args.thread:
    args.thread = int(args.thread.split("/")[-1])

# Create the BlueBird object
bluebird = BlueBird()

# Duplicate the thread
bluebird.duplicate_thread(tweet_id=args.thread)
