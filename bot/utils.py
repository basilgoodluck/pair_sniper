from telegram import Update
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.config import watch_list
def pairs():
    pairs = list(watch_list.split(","))
    return pairs


