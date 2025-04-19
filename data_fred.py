import httpx
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

    response = httpx.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    observations = data.get("observations", [])
    df = pd.DataFrame(observations)
    if not df.empty:
        df = df[["date", "value"]]
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df.dropna(inplace=True)

    return df



# def download_current_fred(series_id: str):
#     """
#     Get the most recent value for the given series ID from FRED.

#     Parameters:
#         series_id (str): The FRED series ID.

#     Returns:
#         pd.DataFrame: A DataFrame containing the most recent observation.
#     """
#     if FRED_API_KEY is None:
#         raise ValueError("FRED access not configured.")

#     url = f"https://api.stlouisfed.org/fred/series/observations"
#     params = {
#         "series_id": series_id,
#         "api_key": FRED_API_KEY,
#         "file_type": "json",
#         "sort_order": "desc",
#         "limit": 1
#     }

#     response = httpx.get(url, params=params)
#     response.raise_for_status()
#     data = response.json()

#     observations = data.get("observations", [])
#     df = pd.DataFrame(observations)
#     if not df.empty:
#         df = df[["date", "value"]]
#         df["date"] = pd.to_datetime(df["date"])
#         df["value"] = pd.to_numeric(df["value"], errors="coerce")
#         df.dropna(inplace=True)

#     return df




if __name__ == "__main__":
    # test usage
    start_date = "2025-02-20"
    end_date = "2025-04-20"
    df = download_from_fred(start_date, end_date, "USEPUINDXD")
    print(df)