from __future__ import absolute_import

from pkg_resources import get_distribution

from pytest import mark

from orphanage import __version__ as orphanage_version


@mark.xfail
def test_distribution():
    distribution = get_distribution('orphanage')
    assert distribution.version == orphanage_version
