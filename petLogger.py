import logging
import os
from datetime import datetime

class PetLogger:
    logger = None
    ch = None
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PetLogger, cls).__new__(cls)
        return cls.instance
    
    @classmethod
    def makeLogger(cls):
        if not cls.logger:
            cls.logger = logging.getLogger('__name__')
            cls.logger.setLevel(logging.INFO)
            fh = logging.FileHandler(os.getcwd() + '/LogFiles/petLog.log')
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            cls.logger.addHandler(fh)
            cls.logger.addHandler(ch)
    
    @classmethod
    def getLogger(cls):
        cls.makeLogger()
        return cls.logger

# critical>error>warning>info>debug