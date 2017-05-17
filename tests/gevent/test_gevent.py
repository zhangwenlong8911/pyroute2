'''
Eventlet compatibility tests.
'''
import uuid
from nose.plugins.skip import SkipTest
from utils import require_user
try:
    from gevent import monkey
except ImportError:
    raise SkipTest('gevent library is not installed')
from pyroute2.config.asyncio import asyncio_config
from pyroute2 import IPRoute
from pyroute2 import NetNS
from pyroute2 import IPDB

monkey.patch_all()
asyncio_config()


class TestBasic(object):

    def test_iproute(self):
        ip = IPRoute()
        try:
            assert len(ip.get_links()) > 1
        except:
            raise
        finally:
            ip.close()

    def test_netns(self):
        require_user('root')
        ns = NetNS(str(uuid.uuid4()))
        try:
            assert len(ns.get_links()) > 1
        except:
            raise
        finally:
            ns.close()
            ns.remove()

    def test_ipdb(self):
        require_user('root')
        ip = IPDB()
        try:
            assert ip._nl_async is False
            assert len(ip.interfaces.keys()) > 1
        except:
            raise
        finally:
            ip.release()
