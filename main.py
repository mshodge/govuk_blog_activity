import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

def get_active_dates(url):
    """Fetch all datetime entries within the last 6 months from the 'time' elements on a given URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    time_elements = soup.find_all('time')
    dates = []
    six_months_ago = datetime.now(timezone.utc) - timedelta(days=6*30)

    for time_elem in time_elements:
        if time_elem.has_attr('datetime'):
            try:
                date = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                if date > six_months_ago:
                    dates.append(date)
            except ValueError:
                pass

    return dates

def scrape_links(base_url):
    """Scrape links and the active dates from each page."""
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links within the specified div
    links = soup.find('ul', class_='blogs-list').find_all('a', href=True)

    data = []

    for link in links:
        link_text = link.get_text(strip=True)
        link_url = link['href']
        full_url = link_url if link_url.startswith('http') else base_url + link_url

        active_dates = get_active_dates(full_url)
        activity_bar = "".join("\u25AE" for _ in active_dates)  # Unicode bar chart for activity

        data.append({
            'Link Text': link_text,
            'URL': f"[{full_url}]({full_url})",
            'Active Dates Count': len(active_dates),
            'Activity': activity_bar
        })
        time.sleep(5)

        print(f"Blog {link_text} activity level: {len(active_dates)} updates in the last six months")

    return data

def save_to_markdown(data, filename):
    """Save the results to a Markdown file."""
    df = pd.DataFrame(data)
    with open(filename, 'w') as f:
        f.write("# GOV.UK Blogs Activity\n\n")
        f.write("This report contains the scraped links, their update frequency within the last 6 months, "
                "and their activity levels.\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n\n")
        f.write("### Notes\n")
        f.write("- `Active Dates Count` indicates how many updates were made within the last 6 months (10 is the max as the scraper only loads the first page).\n")
        f.write("- `Activity` provides a visual representation of the updates using a bar chart. "
                "Each bar represents one update.\n")
        f.write("- This method has not been verified or checked, please do not assume results are 100% correct.\n")
        f.write("- Requests are limited to every 5 seconds inline with fair use policies.\n")
        f.write("\n\n")
        f.write("### Issues\n")
        f.write("If you see an issue where the scraper is not properly collecting data from a blog, "
                "please raise an Issue.\n")

def main():
    base_url = "https://www.blog.gov.uk/?department=&contains="
    data = scrape_links(base_url)

    # Convert the data to a DataFrame for better readability
    df = pd.DataFrame(data)
    print(df)

    # Save the results to a Markdown file
    save_to_markdown(data, "README.md")

if __name__ == "__main__":
    main()
