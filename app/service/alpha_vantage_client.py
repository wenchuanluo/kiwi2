from dataclasses import dataclass

import requests
from flask import current_app

from app import cache

BASE_URL = "https://www.alphavantage.co/query"


@dataclass
class SecurityQuote:
    ticker: str
    date: str
    price: float
    issuer: str


def _get_api_key() -> str:
    """Retrieve the Alpha Vantage API key from application config."""
    api_key = current_app.config.get("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        current_app.logger.error("Alpha Vantage API key is missing from app config.")
        raise RuntimeError("ALPHA_VANTAGE_API_KEY is not configured.")

    return api_key


def get_price_data(ticker: str) -> dict | None:
    """
    Fetch latest price data for the given ticker from Alpha Vantage.

    Returns a dictionary with:
    - price
    - date
    - open
    - high
    - low
    - volume

    Returns None if data is unavailable or the ticker cannot be resolved.
    """
    cache_key = f"price_data:{ticker}"

    cached_value = cache.get(cache_key)
    if cached_value is not None:
        current_app.logger.info(f"Price data for {ticker} found in cache.")
        return cached_value

    api_key = _get_api_key()
    url = BASE_URL

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": api_key,
    }

    try:
        current_app.logger.info(f"Getting price data for ticker: {ticker}")

        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()

        data = response.json()
        quote_data = data.get("Global Quote", {})

        if not quote_data:
            current_app.logger.error(f"No quote data returned for ticker: {ticker}")
            return None

        price = quote_data.get("05. price")
        date = quote_data.get("07. latest trading day")

        if not price or not date:
            current_app.logger.error(f"Missing required price fields for ticker: {ticker}")
            return None

        price_data = {
            "price": float(price),
            "date": date,
            "open": float(quote_data.get("02. open", 0.0)),
            "high": float(quote_data.get("03. high", 0.0)),
            "low": float(quote_data.get("04. low", 0.0)),
            "volume": int(float(quote_data.get("06. volume", 0))),
        }

        cache.set(cache_key, price_data)
        return price_data

    except requests.RequestException as error:
        current_app.logger.error(
            f"Error fetching price data from Alpha Vantage API for ticker {ticker}: {str(error)}"
        )
        return None
    except (ValueError, TypeError) as error:
        current_app.logger.error(
            f"Error parsing price data for ticker {ticker}: {str(error)}"
        )
        return None


def get_company_name(ticker: str) -> str | None:
    """
    Fetch the issuer/company name for the given ticker from Alpha Vantage.

    Returns the company name as a string, or None if no match is found.
    """
    cache_key = f"company_name:{ticker}"

    cached_value = cache.get(cache_key)
    if cached_value is not None:
        current_app.logger.info(f"Company name for {ticker} found in cache.")
        return cached_value

    api_key = _get_api_key()
    url = BASE_URL

    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": ticker,
        "apikey": api_key,
    }

    try:
        current_app.logger.info(f"Getting company details for ticker: {ticker}")

        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()

        data = response.json()
        best_matches = data.get("bestMatches", [])

        if not best_matches:
            current_app.logger.error(f"No company match found for ticker: {ticker}")
            return None

        company_name = best_matches[0].get("2. name")

        if not company_name:
            current_app.logger.error(f"Missing company name in API response for ticker: {ticker}")
            return None

        cache.set(cache_key, company_name)
        return company_name

    except requests.RequestException as error:
        current_app.logger.error(
            f"Error fetching company info for ticker {ticker}: {str(error)}"
        )
        return None


def get_quote(ticker: str) -> SecurityQuote | None:
    """
    Fetch both company name and latest price data, then combine them
    into a SecurityQuote object.

    Returns None if the ticker cannot be resolved.
    """
    company_name = get_company_name(ticker)
    price_data = get_price_data(ticker)

    if company_name is None or price_data is None:
        return None

    return SecurityQuote(
        ticker=ticker,
        date=price_data.get("date"),
        price=price_data.get("price"),
        issuer=company_name,
    )
