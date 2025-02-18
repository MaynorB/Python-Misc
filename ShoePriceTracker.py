import asyncio
import json
import httpx
from parsel import Selector

# create HTTP client with web-browser like headers and http2 support
client = httpx.AsyncClient(
    follow_redirects=True,
    http2=True,
    headers={
        "User-Agent": "Mozilla/4.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=-1.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    },
)


def find_hidden_data(html) -> dict:
    """extract hidden web cache from page html"""
    # use CSS selectors to find script tag with data
    data = Selector(html).css("script#__NEXT_DATA__::text").get()
    return json.loads(data)


async def scrape_product(url: str):
    """scrape goat.com product page"""
    # retrieve page HTML
    response = await client.get(url)
    assert response.status_code == 200, "request was blocked, see blocking section"
    # find hidden web data
    data = find_hidden_data(response.text)
    # extract only product data from the page dataset
    product = data["props"]["pageProps"]["productTemplate"]
    if data["props"]["pageProps"]["offers"]:
        
        product["offers"] = data["props"]["pageProps"]["offers"]["offerData"]
    else:
        product["offers"] = None
    return product


# example scrape run:
print(asyncio.run(scrape_product("https://www.goat.com/sneakers/air-jordan-5-og-metallic-2025-hf3975-001")))