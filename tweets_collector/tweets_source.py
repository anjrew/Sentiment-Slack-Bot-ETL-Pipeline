from abc import ABC, abstractmethod
 
class TweetsSource(ABC):
    """An interface for a tweet source

    Args:
        ABC (ABCMeta): The abstract class
    """
 
    @abstractmethod
    def on_tweet(self) -> dict:
        """The function that is called when a new tweet is received to be emitted to the subscriber

        Returns:
            dict: The tweet dictionary
        """
        pass
    
    @abstractmethod
    def filter(self):
        """A method for filtering tweets by the given rules and to initialize the tweet stream"""
        pass
    
    @abstractmethod
    def add_filter_rules(self, rules):
        """A method for adding a tweet rules to the tweet stream for filtering
         Args:
            rules (list): A list of rules for filtering in. For more information see [this link](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule)
        """
        pass