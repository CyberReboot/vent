import pytest

from ..service_urls import get_urls

def test_url():
    """ Tests get_urls """
    get_urls.url("elasticsearch", "head")
    get_urls.url("elasticsearch", "marvel")
    get_urls.url("aaa-rabbitmq", "")
    get_urls.url("rq-dashboard","")
