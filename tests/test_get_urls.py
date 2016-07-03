import pytest

from ..service_urls import get_urls

def test_url():
    get_urls.url("elasticsearch", "head")
