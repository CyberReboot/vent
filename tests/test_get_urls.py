import pytest

from ..service_urls import get_urls

def test_url():
    get_urls.url("elasticsearch", "head")
    get_urls.url("elasticsearch", "marvel")
    get_urls.url("aaa-rabbitmq", "")
    get_urls.url("rq-dashboard","")
