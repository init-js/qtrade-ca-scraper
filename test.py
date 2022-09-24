#!/usr/bin/env python3
# 
from qtrove import Client

import logging
import os
logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))


cli = Client()
cli.connect()
cli.get_accounts()
