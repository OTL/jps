import os

import jps


def test_get_master_host():
    assert jps.env.get_master_host() == jps.common.DEFAULT_HOST
    os.environ['JPS_MASTER_HOST'] = 'host1'
    assert jps.env.get_master_host() == 'host1'
    del os.environ['JPS_MASTER_HOST']


def test_get_topic_suffix():
    assert jps.env.get_topic_suffix() == ''
    os.environ['JPS_SUFFIX'] = '.aaa'
    assert jps.env.get_topic_suffix() == '.aaa'
    del os.environ['JPS_SUFFIX']
