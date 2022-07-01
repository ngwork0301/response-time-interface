import pytest
from response_times import ResponseTimes

@pytest.fixture
def response_time_instance(request):
    return ResponseTimes("test.csv")

def test_find_failure(response_time_instance):
    expect = [{"address": "10.20.30.1/16", "period": "20221019133324-20221019133325"}]
    assert response_time_instance.find_failure() == expect
