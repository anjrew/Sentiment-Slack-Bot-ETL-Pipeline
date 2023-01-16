import re
import numpy as np

def remove_pattern(input_txt:str, pattern:str):
    """ Removes the given pattern from the input"""
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)
    return input_txt

def clean_tweet(tweet:str) -> str:
    """ Cleans up unused characters from tweets"""
    #remove twitter Return handles (RT @:)*
    tweet = remove_pattern(tweet, "RT @[\w]*:")
    
    tweet = remove_pattern(tweet, "#")

    #remove twitter handles (@)*
    tweet = remove_pattern(tweet, "@[\w]*")

    #remove URL links (http)*
    tweet = remove_pattern(tweet, "https?://[A-Za-z0-9./]*")

    #remove special characters, numbers, punctuations (except for #)*
    tweet = np.core.defchararray.replace([tweet], "[^a-zA-Z]", " ")[0]
    
    return tweet
