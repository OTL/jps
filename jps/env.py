import os


def get_topic_suffix():
    return os.environ.get('JPS_SUFFIX', '')

def get_topic_prefix():
    return os.environ.get('JPS_PREFIX', '')
