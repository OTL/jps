import os
from .common import DEFAULT_HOST

def get_topic_suffix():
    return os.environ.get('JPS_SUFFIX', '')

def get_topic_prefix():
    return os.environ.get('JPS_PREFIX', '')

def get_master_host():
    return os.environ.get('JPS_MASTER_HOST', DEFAULT_HOST)
