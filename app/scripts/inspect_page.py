import asyncio
import json
from app.services.accessibility.analytics.browser_to_json_parser.browser_to_json_parser import fetch_page
from app.services.accessibility.collector import run_extractors
from app.utils.playwright_utils import startup_browser, shutdown_browser

async def main():
    url = "https://example.com"  # Replace with your URL

    # Start the Playwright browser
    await startup_browser()

    try:
        # Fetch the page
        raw_data = await fetch_page(url)
        raw_elements = raw_data["elements"]

        # Run all extractors
        extracted_data = run_extractors(raw_elements)

        # Print nicely
        print(json.dumps(extracted_data, indent=2))

    finally:
        # Always close the browser
        await shutdown_browser()

if __name__ == "__main__":
    asyncio.run(main())
