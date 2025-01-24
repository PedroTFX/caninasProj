from os import wait
import requests
from bs4 import BeautifulSoup
import urllib.parse

def fetch_html(url, headers):
    """Fetch the HTML content from a given URL."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch the URL. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
    return None

def get_total_results(html_content):
    """Parse the HTML content to extract the total number of results."""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Locate the element that contains the total number of results
    result_stats = soup.find("div", id="gs_ab_md")
    if result_stats:
        # Extract and process the text (e.g., "About 1,230 results")
        text = result_stats.get_text()
        print(f"Extracted text: {text}")
        # Extract the numeric part using simple parsing
        numbers = ''.join(filter(str.isdigit, text))
        return int(numbers) if numbers else 0
    else:
        print("Could not find the total results element in the HTML.")
    return 0

def construct_scholar_url(query, exclude=None, source=None, start_year=None, end_year=None):
    """Construct the Google Scholar search URL based on user inputs."""
    base_url = "https://scholar.google.com/scholar"
    params = {
        "hl": "pt-PT",         # Interface language
        "as_sdt": "0,5",       # Standard search settings
        "q": query,            # Search query
        "as_vis": "1",         # Include only results with preview available
    }
    if exclude:
        params["q"] += f", -{exclude}"
    if source:
        params["q"] += f" source:{source}"
    if start_year:
        params["as_ylo"] = start_year
    if end_year:
        params["as_yhi"] = end_year

    # Encode parameters into the URL
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def main():
    # User-configurable search parameters
    query = 'Bayes OR bayesian OR MCMC'
    exclude = ""
    source = "Ecology"
    start_year = 1991
    # end_year = start_year + 1 

    for i in range(36):
        wait()
        # Construct the search URL
        url = construct_scholar_url(query, exclude=exclude, source=source, start_year= str(start_year), end_year=str(start_year))
        # print(f"Generated search URL: {url}")
        print("start " + str(start_year))
        # Set headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Fetch and parse the HTML content
        # print("Fetching HTML content...")
        html_content = fetch_html(url, headers)
        if html_content:
            # print("HTML content fetched successfully. Parsing total results...")
            total_results = get_total_results(html_content)
            # print(f"Total results found: {total_results}")
        else:
            print("Failed to fetch or parse the HTML content.")
        
        start_year += 1

if __name__ == "__main__":
    main()
