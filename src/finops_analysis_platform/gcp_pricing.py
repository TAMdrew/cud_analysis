# src/finops_analysis_platform/gcp_pricing.py

import json
import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class GcpSkuFetcher:
    """
    A class to fetch and analyze Google Cloud Platform SKU pricing,
    specifically for Compute Engine CUDs.
    """

    BASE_URL = "https://cloudbilling.googleapis.com/v1"
    COMPUTE_ENGINE_SERVICE_ID = "6F81-5844-456A"

    # Note: These SKU IDs may change over time or new ones may be added.
    # It is recommended to periodically review and update this dictionary
    # to ensure accuracy.
    NEW_MODEL_SKU_IDS = {
        "B22F-51BE-D599": "New Model - 3 Year Flexible CUD",
        "5515-81A8-03A2": "New Model - 1 Year Flexible CUD",
    }

    def __init__(self, api_key: str):
        """
        Initializes the fetcher with a GCP API key.

        Args:
            api_key: Your GCP API key.
        """
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self.api_key = api_key

    def get_all_skus(self, service_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches all SKUs for a given service, handling pagination.

        Args:
            service_id: The ID of the service (e.g., Compute Engine's ID).

        Returns:
            A list of SKU dictionaries, or None if an API error occurs.
        """
        all_skus: List[Dict[str, Any]] = []
        page_token: Optional[str] = None
        url = f"{self.BASE_URL}/services/{service_id}/skus"

        logger.info(
            "Fetching all SKUs for service %s (this may take a moment)...", service_id
        )

        while True:
            params = {"key": self.api_key}
            if page_token:
                params["pageToken"] = page_token

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                all_skus.extend(data.get("skus", []))

                page_token = data.get("nextPageToken")
                if not page_token:
                    break
            except requests.exceptions.RequestException as e:
                logger.error("An error occurred while calling the API: %s", e)
                if e.response:
                    try:
                        error_details = e.response.json()
                        logger.error(
                            "API Error Response: %s",
                            json.dumps(error_details, indent=2),
                        )
                    except (ValueError, AttributeError):
                        logger.error("Raw Error Response Text: %s", e.response.text)
                else:
                    logger.error("No response received from the server.")
                return None

        logger.info("Finished fetching. Total SKUs found: %d", len(all_skus))
        return all_skus

    def analyze_cud_prices(self) -> List[Dict[str, Any]]:
        """
        Finds and returns pricing details for both old and new CUD models.

        Returns:
            A list of dictionaries, where each dictionary contains the
            details of a relevant CUD SKU.
        """
        all_skus = self.get_all_skus(self.COMPUTE_ENGINE_SERVICE_ID)
        if not all_skus:
            return []

        logger.info("Analyzing CUD SKUs...")
        found_skus_data: List[Dict[str, Any]] = []

        for sku in all_skus:
            sku_id = sku.get("skuId", "")
            description = sku.get("description", "")

            is_old_model = "Commitment - dollar based" in description
            is_new_model = sku_id in self.NEW_MODEL_SKU_IDS

            if is_old_model or is_new_model:
                model_type = (
                    "Old Model" if is_old_model else self.NEW_MODEL_SKU_IDS.get(sku_id)
                )

                sku_details: Dict[str, Any] = {
                    "description": description,
                    "model_type": model_type,
                    "sku_id": sku_id,
                    "usage_type": sku.get("category", {}).get("usageType", "N/A"),
                    "pricing": [],
                }

                for pricing_info in sku.get("pricingInfo", []):
                    pricing_expression = pricing_info.get("pricingExpression", {})

                    price_entry: Dict[str, Any] = {
                        "summary": pricing_info.get("summary", ""),
                        "usage_unit": pricing_expression.get(
                            "usageUnitDescription", ""
                        ),
                    }

                    for rate in pricing_expression.get("tieredRates", []):
                        unit_price = rate.get("unitPrice", {})
                        currency = unit_price.get("currencyCode", "N/A")
                        nanos = unit_price.get("nanos", 0) or 0
                        units = unit_price.get("units", 0) or 0

                        try:
                            price = float(units) + (float(nanos) / 1_000_000_000)
                            price_entry["price"] = f"{price:.10f}"
                            price_entry["currency"] = currency
                        except (ValueError, TypeError):
                            price_entry["price"] = "N/A"
                            price_entry["currency"] = "N/A"

                    sku_details["pricing"].append(price_entry)

                found_skus_data.append(sku_details)

        if not found_skus_data:
            logger.info("No matching CUD SKUs (old or new model) were found.")

        return found_skus_data
