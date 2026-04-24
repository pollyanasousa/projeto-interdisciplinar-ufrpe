"""
This file contains the functions to deal with IO (input/output).
"""

import re

def inputint(msg):
    """
    It asks for an integer and returns the int the user typed. The variable msg is the message displayed on the screen. While the user does not type a valid int, the function keeps prompting him.
    """

    ret = ""
    while not bool(re.match(r"^[-+]?\d+$", ret)):
        ret = input(msg)

    return int(ret)
