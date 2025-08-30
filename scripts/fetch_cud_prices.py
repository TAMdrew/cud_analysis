# scripts/fetch_cud_prices.py

import os
import sys

import pandas as pd

# Add the src directory to the Python path to allow importing the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from finops_analysis_platform.gcp_pricing import GcpSkuFetcher


def main():
    """
    Fetches and analyzes CUD prices using the GcpSkuFetcher.
    """
    # For security, load the API key from an environment variable.
    api_key = os.getenv("CLOUD_BILLING_API_KEY")

    if not api_key:
        print("ERROR: CLOUD_BILLING_API_KEY environment variable not set.")
        print(
            "Please set it by running: export CLOUD_BILLING_API_KEY='your_api_key_here'"
        )
        sys.exit(1)

    print("Initializing SKU fetcher...")
    sku_fetcher = GcpSkuFetcher(api_key=api_key)

    # Fetch and analyze CUD prices
    cud_data = sku_fetcher.analyze_cud_prices()

    if cud_data:
        # For better analysis, load the data into a pandas DataFrame
        df_cud_prices = pd.json_normalize(
            cud_data,
            record_path=["pricing"],
            meta=["description", "model_type", "sku_id"],
        )
        print("\n--- CUD Pricing Analysis ---")
        # Print the relevant columns of the DataFrame
        print(
            df_cud_prices[
                [
                    "model_type",
                    "description",
                    "sku_id",
                    "price",
                    "currency",
                    "usage_unit",
                ]
            ].to_string()
        )
    else:
        print("\nNo CUD pricing data was found.")


if __name__ == "__main__":
    main()
