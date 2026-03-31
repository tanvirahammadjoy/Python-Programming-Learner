"""
=============================================================
  Web Scraper: Books to Scrape (books.toscrape.com)
  Tools: requests + BeautifulSoup4
  Output: books_data.csv  &  books_data.json
=============================================================

HOW TO FIND CSS SELECTORS WITH BROWSER DEVTOOLS
------------------------------------------------
1. Open the target page in Chrome / Firefox.
2. Right-click any element you want → "Inspect" (or F12).
3. In the Elements panel, hover over tags until the element
   highlights on the page.
4. Right-click the tag → Copy → Copy selector  (Chrome)
   or  Copy → CSS Selector  (Firefox).
5. Paste that selector into soup.select("...") to target it.

Tips:
  • A dot (.) prefix means a CSS class  → .price_color
  • A hash (#) prefix means an id       → #my-id
  • Tag + class together                → article.product_pod
  • Descendant (space)                  → div.product_main p.price_color
  • Attribute selector                  → a[href]

INSTALL DEPENDENCIES
--------------------
    pip install requests beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import re


# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
BASE_URL    = "https://books.toscrape.com/catalogue/"
START_URL   = "https://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES   = 5          # Scrape the first 5 pages (50 books total)
REQUEST_DELAY = 1.0      # Seconds to wait between requests (be polite!)
CSV_OUTPUT  = "books_data.csv"
JSON_OUTPUT = "books_data.json"

# HTTP headers – some servers reject requests without a User-Agent
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; PythonScraper/1.0; "
        "+https://github.com/example/scraper)"
    )
}


# ------------------------------------------------------------------
# HELPER: fetch a single page safely
# ------------------------------------------------------------------
def fetch_page(url: str) -> BeautifulSoup | None:
    """
    Download a URL and return a BeautifulSoup object, or None on failure.

    Handles common errors:
      - Network timeouts
      - Non-200 HTTP status codes (404, 500, etc.)
      - Connection errors (DNS failure, refused connection)
    """
    try:
        # timeout=(connect_seconds, read_seconds) – never hang forever
        response = requests.get(url, headers=HEADERS, timeout=(5, 10))

        # raise_for_status() throws an HTTPError for 4xx / 5xx responses
        response.raise_for_status()

        # Parse the HTML with the built-in html.parser (no extra install)
        # Alternatives: "lxml" (faster), "html5lib" (more lenient)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Could not connect to {url}")
    except requests.exceptions.Timeout:
        print(f"[ERROR] Request timed out for {url}")
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error {e.response.status_code} for {url}")
    except requests.exceptions.RequestException as e:
        # Catch-all for any other requests-related error
        print(f"[ERROR] Unexpected error for {url}: {e}")

    return None  # Caller must check for None before using the result


# ------------------------------------------------------------------
# HELPER: parse star rating from CSS class name
# ------------------------------------------------------------------
def parse_star_rating(article_tag) -> int:
    """
    The star rating is encoded as a CSS class on a <p> tag:
        <p class="star-rating Three">

    soup.find() locates the FIRST matching tag inside `article_tag`.
    We grab the second class word and convert it to a number.
    """
    word_to_num = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    # soup.find(tag, attrs)  – find ONE element by tag + attribute dict
    rating_tag = article_tag.find("p", class_="star-rating")

    if rating_tag:
        # .get("class") returns a list, e.g. ["star-rating", "Three"]
        classes = rating_tag.get("class", [])
        for cls in classes:
            if cls in word_to_num:
                return word_to_num[cls]

    return 0  # Unknown / missing rating


# ------------------------------------------------------------------
# CORE: scrape all books from one listing page
# ------------------------------------------------------------------
def scrape_listing_page(soup: BeautifulSoup) -> list[dict]:
    """
    Extract book data from a catalogue listing page.

    soup.select(css_selector) returns a LIST of all matching tags.
    soup.find(tag)            returns the FIRST matching tag (or None).

    Key CSS selectors used here (verify with DevTools):
      article.product_pod          → each book card
      h3 > a                       → title (inside h3, inside article)
      p.price_color                → price text
      p.instock.availability       → stock status
      p.star-rating                → star rating (class encodes value)
    """
    books = []

    # soup.select() with a CSS selector – returns a list (possibly empty)
    # "article.product_pod" means: <article> tags with class "product_pod"
    book_cards = soup.select("article.product_pod")

    print(f"  Found {len(book_cards)} book cards on this page.")

    for card in book_cards:
        # ── TITLE ────────────────────────────────────────────────────
        # The title lives in:  <h3><a href="..." title="Full Title">…</a></h3>
        # The visible text is truncated; the full title is in the `title` attr.
        #
        # card.find("h3") → finds the <h3> tag inside this card
        # .find("a")      → finds the <a> inside that <h3>
        # .get("title")   → reads the HTML attribute value (full title)
        h3_tag  = card.find("h3")
        a_tag   = h3_tag.find("a") if h3_tag else None
        title   = a_tag.get("title", "").strip() if a_tag else "N/A"

        # ── LINK ─────────────────────────────────────────────────────
        # href is relative (e.g. "catalogue/book-name/index.html")
        # We prepend BASE_URL to build the absolute URL.
        relative_href = a_tag.get("href", "") if a_tag else ""
        # Some hrefs start with "../" – clean that up
        clean_href = relative_href.lstrip("./")
        full_link  = BASE_URL + clean_href if clean_href else "N/A"

        # ── PRICE ────────────────────────────────────────────────────
        # <p class="price_color">£51.77</p>
        #
        # card.select_one() is like find() but takes a CSS selector string.
        price_tag  = card.select_one("p.price_color")
        price_text = price_tag.get_text(strip=True) if price_tag else "N/A"

        # Convert "£51.77" → float 51.77 for numeric operations later
        price_float = None
        if price_text != "N/A":
            # re.sub removes any non-numeric character except "."
            numeric_str = re.sub(r"[^\d.]", "", price_text)
            try:
                price_float = float(numeric_str)
            except ValueError:
                price_float = None  # Conversion failed – keep as None

        # ── AVAILABILITY ─────────────────────────────────────────────
        # <p class="instock availability"> In stock </p>
        stock_tag    = card.select_one("p.instock.availability")
        # .get_text(strip=True) strips leading/trailing whitespace
        availability = stock_tag.get_text(strip=True) if stock_tag else "Unknown"

        # ── STAR RATING ──────────────────────────────────────────────
        stars = parse_star_rating(card)

        books.append({
            "title":        title,
            "price_text":   price_text,     # original string e.g. "£51.77"
            "price_gbp":    price_float,    # numeric float e.g. 51.77
            "availability": availability,
            "stars":        stars,
            "link":         full_link,
        })

    return books


# ------------------------------------------------------------------
# CORE: find the "next page" link on a listing page
# ------------------------------------------------------------------
def get_next_page_url(soup: BeautifulSoup) -> str | None:
    """
    The pagination section looks like:
        <li class="next"><a href="page-2.html">next</a></li>

    Returns the absolute URL of the next page, or None if on last page.
    """
    # soup.select_one() is equivalent to soup.find() but uses CSS selectors
    next_btn = soup.select_one("li.next a")

    if next_btn:
        next_href = next_btn.get("href", "")
        return BASE_URL + next_href  # Absolute URL

    return None  # No "next" button means we're on the last page


# ------------------------------------------------------------------
# SAVE: write results to CSV
# ------------------------------------------------------------------
def save_to_csv(books: list[dict], filename: str) -> None:
    """
    Write a list of dicts to a CSV file.
    csv.DictWriter uses the dict keys as column headers automatically.
    """
    if not books:
        print("[WARN] No books to save.")
        return

    fieldnames = books[0].keys()  # Column order = insertion order (Python 3.7+)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()       # Write the header row
        writer.writerows(books)    # Write all data rows at once

    print(f"[CSV] Saved {len(books)} records → {filename}")


# ------------------------------------------------------------------
# SAVE: write results to JSON
# ------------------------------------------------------------------
def save_to_json(books: list[dict], filename: str) -> None:
    """
    Write a list of dicts to a pretty-printed JSON file.
    indent=2 makes it human-readable; ensure_ascii=False preserves
    characters like £ without escaping them.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)

    print(f"[JSON] Saved {len(books)} records → {filename}")


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    all_books   = []
    current_url = START_URL
    page_num    = 1

    print(f"Starting scrape – up to {MAX_PAGES} pages\n{'─'*50}")

    while current_url and page_num <= MAX_PAGES:
        print(f"Page {page_num}: {current_url}")

        soup = fetch_page(current_url)

        if soup is None:
            # fetch_page already printed the error; stop gracefully
            print("[STOP] Aborting due to fetch error.")
            break

        # Extract books from this page and accumulate them
        books_on_page = scrape_listing_page(soup)
        all_books.extend(books_on_page)

        # Find the URL of the next page (returns None on the last page)
        current_url = get_next_page_url(soup)
        page_num   += 1

        # Polite delay – don't hammer the server
        if current_url:
            time.sleep(REQUEST_DELAY)

    print(f"\n{'─'*50}")
    print(f"Total books scraped: {len(all_books)}")

    # ── SAVE RESULTS ────────────────────────────────────────────────
    if all_books:
        save_to_csv(all_books,  CSV_OUTPUT)
        save_to_json(all_books, JSON_OUTPUT)

        # ── QUICK STATS ─────────────────────────────────────────────
        prices = [b["price_gbp"] for b in all_books if b["price_gbp"] is not None]
        if prices:
            print(f"\nPrice stats (GBP):")
            print(f"  Min : £{min(prices):.2f}")
            print(f"  Max : £{max(prices):.2f}")
            print(f"  Avg : £{sum(prices)/len(prices):.2f}")


if __name__ == "__main__":
    main()