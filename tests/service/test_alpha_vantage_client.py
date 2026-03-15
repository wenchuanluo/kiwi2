from unittest.mock import Mock

import requests

from app.service.alpha_vantage_client import get_company_name, get_price_data


def test_get_company_name_returns_company_name_on_success(app, monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "bestMatches": [
            {
                "1. symbol": "AAPL",
                "2. name": "Apple Inc.",
            }
        ]
    }

    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", mock_get)
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value=None))
    mock_cache_set = Mock()
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.set", mock_cache_set)

    result = get_company_name("AAPL")

    assert result == "Apple Inc."
    mock_get.assert_called_once()
    mock_cache_set.assert_called_once_with("company_name:AAPL", "Apple Inc.")


def test_get_company_name_returns_none_for_empty_response(app, monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"bestMatches": []}

    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", Mock(return_value=mock_response))
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value=None))

    result = get_company_name("UNKNOWN")

    assert result is None


def test_get_company_name_returns_none_when_name_missing(app, monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "bestMatches": [
            {
                "1. symbol": "AAPL"
            }
        ]
    }

    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", Mock(return_value=mock_response))
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value=None))

    result = get_company_name("AAPL")

    assert result is None


def test_get_company_name_cache_hit_skips_api_call(app, monkeypatch):
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value="Apple Inc."))
    mock_get = Mock()
    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", mock_get)

    result = get_company_name("AAPL")

    assert result == "Apple Inc."
    mock_get.assert_not_called()


def test_get_company_name_request_exception_returns_none(app, monkeypatch):
    mock_get = Mock(side_effect=requests.RequestException("API failure"))
    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", mock_get)
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value=None))

    result = get_company_name("AAPL")

    assert result is None


def test_get_price_data_returns_price_data_on_success(app, monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "Global Quote": {
            "01. symbol": "AAPL",
            "02. open": "149.50",
            "03. high": "151.00",
            "04. low": "148.75",
            "05. price": "150.25",
            "06. volume": "1234567",
            "07. latest trading day": "2026-03-14",
        }
    }

    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", mock_get)
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value=None))
    mock_cache_set = Mock()
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.set", mock_cache_set)

    result = get_price_data("AAPL")

    assert result == {
        "price": 150.25,
        "date": "2026-03-14",
        "open": 149.50,
        "high": 151.00,
        "low": 148.75,
        "volume": 1234567,
    }
    mock_get.assert_called_once()
    mock_cache_set.assert_called_once_with(
        "price_data:AAPL",
        {
            "price": 150.25,
            "date": "2026-03-14",
            "open": 149.50,
            "high": 151.00,
            "low": 148.75,
            "volume": 1234567,
        },
    )


def test_get_price_data_returns_none_for_empty_response(app, monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"Global Quote": {}}

    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", Mock(return_value=mock_response))
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value=None))

    result = get_price_data("UNKNOWN")

    assert result is None


def test_get_price_data_returns_none_when_required_fields_missing(app, monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "Global Quote": {
            "02. open": "149.50",
            "03. high": "151.00",
            "04. low": "148.75",
            "06. volume": "1234567",
        }
    }

    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", Mock(return_value=mock_response))
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value=None))

    result = get_price_data("AAPL")

    assert result is None


def test_get_price_data_cache_hit_skips_api_call(app, monkeypatch):
    cached_price_data = {
        "price": 150.25,
        "date": "2026-03-14",
        "open": 149.50,
        "high": 151.00,
        "low": 148.75,
        "volume": 1234567,
    }

    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value=cached_price_data))
    mock_get = Mock()
    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", mock_get)

    result = get_price_data("AAPL")

    assert result == cached_price_data
    mock_get.assert_not_called()


def test_get_price_data_request_exception_returns_none(app, monkeypatch):
    mock_get = Mock(side_effect=requests.RequestException("API failure"))
    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", mock_get)
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value=None))

    result = get_price_data("AAPL")

    assert result is None


def test_get_price_data_value_error_returns_none(app, monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "Global Quote": {
            "01. symbol": "AAPL",
            "02. open": "not-a-number",
            "03. high": "151.00",
            "04. low": "148.75",
            "05. price": "150.25",
            "06. volume": "1234567",
            "07. latest trading day": "2026-03-14",
        }
    }

    monkeypatch.setattr("app.service.alpha_vantage_client.requests.get", Mock(return_value=mock_response))
    monkeypatch.setattr("app.service.alpha_vantage_client.cache.get", Mock(return_value=None))

    result = get_price_data("AAPL")

    assert result is None