import requests
import pandas as pd
import os



FRED_CATEGORY_URL = "https://api.stlouisfed.org/fred/category"
FRED_SERIES_URL = "https://api.stlouisfed.org/fred/series"

FRED_API_KEY = os.getenv("FRED_API_KEY")


def download_from_fred(start_date: str, end_date: str, series_id: str):
    """
    Download S&P 500 close of day values from FRED.

    Parameters:
        start_date (str): Start date in the format 'YYYY-MM-DD'.
        end_date (str): End date in the format 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame: A DataFrame containing the S&P 500 data.
    """
    if FRED_API_KEY is None:
        raise ValueError("FRED access not configured.")

    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    observations = data.get("observations", [])
    df = pd.DataFrame(observations)
    if not df.empty:
        df = df[["date", "value"]]
        df.rename(columns={"date": "Date", "value": "Close"}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df.dropna(inplace=True)

    return df


if __name__ == "__main__":
    # Example usage
    start_date = "2025-01-01"
    end_date = "2025-04-01"
    df = download_from_fred(start_date, end_date)
    print(df)