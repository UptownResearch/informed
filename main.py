import os
import time
import sys
sys.path.append(os.path.abspath("./src"))
from buyers import get_buyer_list
from collection import get_collections_list
from trades import get_trades_list

# Get all collections dropped so far
get_collections_list()

# Get all trades history for dropped collections so far
time.sleep(3)
get_trades_list()

# Get all buyers who bought NFTs before the collection was dropped.
time.sleep(3)
get_buyer_list()