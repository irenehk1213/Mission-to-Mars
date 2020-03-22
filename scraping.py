from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first <a> tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')
    try:
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    return img_url

def mars_hemisphere(browser):
    # USGS Astrogeology site to obtain high resolution images for each of Mar's hemispheres
    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    # Parse the resulting html with soup
    html = browser.html
    hemisphere_soup = BeautifulSoup(html, 'html.parser')
    # list to store:
    hemisphere_image_urls = []
    # create empty dict
    hemisphere_dict = {}
    # get all the title
    results = hemisphere_soup.find_all('h3')
    for result in results:
        # Get text info from result
        itema = result.text
        browser.click_link_by_partial_text(itema)
        open_elem = browser.find_link_by_partial_text('Open')
        open_elem.click()
        # Parse the resulting html with soup
        htmla = browser.html
        hemi_img_soup = BeautifulSoup(htmla,'html.parser')
        # Grab the image link
        linka = hemi_img_soup.find_all('div', class_="downloads")[0].find_all('a')[0].get("href")
        # Pass title to Dictionary
        hemisphere_dict["title"]=itema
        # Pass url to Dictionary
        hemisphere_dict["img_url"]=linka
        # Append Dictionary to the list 
        hemisphere_image_urls.append(hemisphere_dict)
        # Clean Up Dictionary
        hemisphere_dict = {}
        browser.click_link_by_partial_text('Close')
        browser.back()   
    # Return List
    return hemisphere_image_urls

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html'ß to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()
   
def scrape_all():
   # Initiate headless driver for deployment
    executable_path = {"chromedriver.exe"}
    browser = Browser('chrome', executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)
    print(news_title)
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "mars_hemisphere" : mars_hemisphere(browser),
        "last_modified": dt.datetime.now()
            }
    browser.quit()
    return data

if __name__ == "__main__":
    # If running as script, print scraped data
    print("scraping")
    