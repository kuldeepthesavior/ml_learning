"""Download IPO information published by NSE India.

The NSE response schema changes occasionally.  This module keeps the raw
fields after flattening them, while also exposing common IPO fields in a
stable DataFrame.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
import requests


class NSEIPOData:
    """Client for current, upcoming, and recently closed NSE IPO issues."""

    API_URLS = {
        "current": "https://www.nseindia.com/api/ipo-current-issue",
        "upcoming": "https://www.nseindia.com/api/all-upcoming-issues",
    }

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.nseindia.com/market-data/all-upcoming-issues",
            }
        )

    def _request_json(self, url: str) -> Any:
        """Open the NSE site first so the API request receives NSE cookies."""
        self.session.get("https://www.nseindia.com", timeout=self.timeout)
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _records(payload: Any) -> list[dict[str, Any]]:
        """Find issue records in common NSE response wrappers."""
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if not isinstance(payload, dict):
            return []

        for key in ("data", "records", "ipoData", "issues", "result"):
            if key in payload:
                records = NSEIPOData._records(payload[key])
                if records:
                    return records

        if any(isinstance(value, (str, int, float)) for value in payload.values()):
            return [payload]
        return []

    @staticmethod
    def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
        """Flatten nested dictionaries while retaining list values."""
        flattened: dict[str, Any] = {}
        if not isinstance(value, dict):
            return {prefix: value}

        for key, item in value.items():
            name = f"{prefix}_{key}" if prefix else str(key)
            if isinstance(item, dict):
                flattened.update(NSEIPOData._flatten(item, name))
            else:
                flattened[name] = item
        return flattened

    @staticmethod
    def _number(value: Any) -> float | None:
        """Convert values such as '1,234' and 'Rs 100' to numbers."""
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"[-+]?[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?", str(value))
        return float(match.group(0).replace(",", "")) if match else None

    @classmethod
    def _normalise(cls, records: list[dict[str, Any]], issue_type: str) -> pd.DataFrame:
        rows = [cls._flatten(record) for record in records]
        if not rows:
            return pd.DataFrame()

        frame = pd.DataFrame(rows)
        frame.insert(0, "issue_type", issue_type)

        aliases = {
            "entity_name": ("companyName", "companyname", "issuerName", "name"),
            "symbol": ("symbol", "scripName", "issueSymbol"),
            "price_range": ("priceRange", "priceBand", "issuePrice"),
            "lower_price": ("lowerPrice", "floorPrice", "minPrice"),
            "upper_price": ("upperPrice", "capPrice", "maxPrice"),
            "total_shares": ("totalShares", "issueSize", "sharesOffered", "noOfShares"),
            "lot_size": ("lotSize", "marketLot"),
            "open_date": ("openDate", "issueOpenDate", "biddingStartDate"),
            "close_date": ("closeDate", "issueCloseDate", "biddingEndDate"),
            "listing_date": ("listingDate",),
        }
        lower_columns = {column.lower(): column for column in frame.columns}
        for output, candidates in aliases.items():
            for candidate in candidates:
                source = lower_columns.get(candidate.lower())
                if source:
                    frame[output] = frame[source]
                    break

        for column in ("lower_price", "upper_price", "total_shares"):
            if column in frame:
                frame[column] = frame[column].map(cls._number)

        if "total_shares" in frame and "upper_price" in frame:
            frame["ipo_value"] = frame["total_shares"] * frame["upper_price"]
            frame["ipo_value_unit"] = "INR"

        return frame

    def get_ipos(self, issue_type: str = "current") -> pd.DataFrame:
        """Return IPO details as a DataFrame for ``current`` or ``upcoming``."""
        if issue_type not in self.API_URLS:
            raise ValueError(f"issue_type must be one of {tuple(self.API_URLS)}")
        payload = self._request_json(self.API_URLS[issue_type])
        return self._normalise(self._records(payload), issue_type)

    def get_all_ipos(self) -> pd.DataFrame:
        """Fetch current and upcoming IPOs and combine them."""
        frames = [self.get_ipos(issue_type) for issue_type in self.API_URLS]
        frames = [frame for frame in frames if not frame.empty]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


if __name__ == "__main__":
    ipo_data = NSEIPOData()
    ipos = ipo_data.get_all_ipos()
    print(ipos.to_string(index=False))
    ipos.to_csv("nse_ipo_details.csv", index=False)