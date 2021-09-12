from selenium import webdriver

def main():
    url = "https://dichvucong.gov.vn/p/home/dvc-dich-vu-cong-truc-tuyen-ds.html?pkeyWord=covid"
    driver =  webdriver.Chrome("chromedriver")
    driver.get(url)
    elements = driver.find_elements_by_css_selector("#content_DVCTT_List li")
    for element in elements:
        link = element.find_element_by_css_selector("a").get_attribute("href")
        title = element.find_element_by_css_selector("a").text
        print(title)
        print(link)
    
if __name__ == '__main__':
    main()