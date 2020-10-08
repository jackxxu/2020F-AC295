import sys
import os
import requests
import time
import shutil
from selenium import webdriver

def download_google_images(search_term_list = ["tomato", "bell pepper"], num_images_requested = 10):
    print("download_google_images...")
    start_time = time.time()

    # Setup download folder
    downloads = "dataset"
    if os.path.exists(downloads):
        shutil.rmtree(downloads)
    os.mkdir(downloads)

    # Each scrolls provides 400 image approximately
    number_of_scrolls = int(num_images_requested / 400) + 1

    # Firefox Options
    options = webdriver.FirefoxOptions()
    options.headless = True
    browser = webdriver.Firefox(options=options)

    for search_term in search_term_list:
        print("Searching for :", search_term)
        browser.get('https://www.google.com/search?q=' + search_term)

        # Go to Google Images
        images_links = browser.find_elements_by_xpath('//a[contains(@class, "q qs")]')
        for link in images_links:
            #print(link)
            print(link.get_attribute("href"))

        # Wait
        time.sleep(5)

        # Go to images
        images_link = images_links[0]
        images_link.click()

        for _ in range(number_of_scrolls):
            for __ in range(10):
                # multiple scrolls needed to show all 400 images
                browser.execute_script("window.scrollBy(0, 1000000)")
                time.sleep(2)
            # to load next 400 images
            time.sleep(5)
            # try to find show more results bottom
            try:
                # if found click to load more image
                browser.find_element_by_xpath("//input[@value='Show more results']").click()
            except Exception as e:
                # if not exit
                print("End of page")
                break

        # Image link store
        imgs_urls = set()
        # Find the thumbnail images
        thumbnails = browser.find_elements_by_xpath('//a[@class="wXeWr islib nfEiy mM5pbd"]')
        # loop over the thumbs to retrive the links
        for thumbnail in thumbnails:
            # check if reached the request number of links
            if len(imgs_urls) >= num_images_requested:
                break
            try:
                thumbnail.click()
                time.sleep(2)
            except Exception as error:
                print("Error clicking one thumbnail : ", error)
            # Find the image url
            url_elements = browser.find_elements_by_xpath('//img[@class="n3VNCb"]')
            # check for the correct url
            for url_element in url_elements:
                try:
                    url = url_element.get_attribute('src')
                except e:
                    print("Error getting url")
                if url.startswith('http') and not url.startswith('https://encrypted-tbn0.gstatic.com'):
                    #print("Found image url:", url)
                    imgs_urls.add(url)

        print('Number of image urls found:', len(imgs_urls))

        # Wait 5 seconds
        time.sleep(5)

        # Save the images
        img_dir = os.path.join(downloads, search_term.lower().replace(" ","_"))
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        count = 0
        for url in imgs_urls:
            try:

                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    file_path = os.path.join(img_dir, '{0}.jpg'.format(count))
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    count += 1

                # sleep
                if count % 10 == 0:
                    time.sleep(3)
            except Exception as e:
                print("Error in url:", url)
                print(e)
                continue

    # Quit the browser
    browser.quit()

    execution_time = (time.time() - start_time) / 60.0
    print("Download execution time (mins)", execution_time)
