from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import time
from lxml import etree
import re
from log_reader import read_log
import os


def start_scrape(country_url):

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=300)
        page = browser.new_page()
        page.goto('https://www.enfsolar.com/directory/seller/' + country_url)
        page.is_visible('table.enf-list-table ')
        country_data = page.inner_html('table.enf-list-table ')
        country_data_soup = BeautifulSoup(country_data, 'html.parser')
        rows = country_data_soup.find('tbody').find_all('tr')

        for i in rows:
            is_prem_acc = False
            link = i.find('a')['href']
            if os.access(f"data/{country_url}_log.txt", os.F_OK) is not False:
                already_scraped = read_log(country_url)
            else:
                already_scraped = []
            if link in already_scraped:
                print(f"URL: {link} ALLREADY SCRAPED")
                continue
            else:
                name = i.find('a').text.strip()
                row_data = i.find_all('td')
                area = row_data[3].text.strip()
                try:
                    distrib = row_data[4].find('img')['alt']
                except TypeError:
                    distrib = ""
                brands = row_data[5].text.strip()
                try:
                    minimum_order = row_data[6].text.strip()
                except:
                    minimum_order = ""
                products_main = ", ".join([i['alt'] for i in row_data[7].find_all('img')])

                # Opening page with company data and creating bs object to navigate
                page2 = browser.new_page()
                page2.goto(link)

                # Enable if needed
                try:
                    page2.locator('td[itemprop=telephone]').click()
                except:
                    page2.locator('div[itemprop=telephone]').click()
                # page2.locator('td[itemprop=email]').click()
                try:
                    all_data = page2.inner_html('div.enf-company-profile.merging-company-profile ')
                except:
                    all_data = page2.inner_html('div.enf-company-profile-special.merging-company-profile ')


                all_data_soup = BeautifulSoup(all_data, 'html.parser')
                # print("ALL DATA: ", all_data_soup.prettify())
                try:
                    company_data = page2.inner_html('div.enf-company-profile-info.clearfix')
                except:
                    print("EXCEPT")
                    company_data = page2.inner_html('div.title.content')
                company_data_soup = BeautifulSoup(company_data, 'html.parser')

                # Checking if we enter the right tab in website
                right_tab = all_data_soup.find('span', {'class': 'type_icon type_icon_seller'})
                right_tab_installer = all_data_soup.find('span', {'class': 'type_icon type_icon_installer'})
                # print("RIGHT TAB: ", right_tab)
                # print("RIGHT TAB INSTALLER: ", right_tab_installer)
                if right_tab is not None or right_tab_installer is not None:
                    print("!!!!!!!!!!!!!!!!!CLICKING!!!!!!!")
                    page2.locator('span.type_title >> text=Sellers').click()
                    time.sleep(2)

                try:
                    address = company_data_soup.find('td', {'itemprop': 'address'}).text.strip()
                except:
                    address = all_data_soup.find('div', {'class': 'word', 'itemprop': 'address'}).text.strip()

                try:
                    phone = company_data_soup.find('td', {'itemprop': 'telephone'}).text.strip()
                except:
                    phone = all_data_soup.find('div', {'itemprop': 'telephone'}).text.strip()

                try:
                    email = company_data_soup.find('td', {'itemprop': 'email'}).find('a').text.strip()
                except AttributeError:
                    print("EMAIL ERROR")
                    page2.close()
                    x = input("Type something to resume")
                    page2 = browser.new_page()
                    page2.goto(link)
                    try:
                        page2.locator('td[itemprop=telephone]').click()
                        page2.locator('td[itemprop=email]').click()
                    except:
                        page2.locator('div[itemprop=telephone]').click()
                        page2.locator('div[itemprop=email]').click()
                except:
                    print("Final EXCEPTION EMAIL")
                    email = all_data_soup.find('div', {'itemprop': 'email'}).find('a').text.strip()

                    # Checking if we enter the right tab in website
                    right_tab = all_data_soup.find('span', {'class': 'type_icon type_icon_seller'})
                    print(right_tab)
                    if right_tab is not None or right_tab_installer is not None:
                        print("!!!!!!!!!!!!!!!!!CLICKING!!!!!!!")
                        page2.locator('span.type_title >> text=Sellers').click()
                        time.sleep(2)

                    try:
                        company_data = page2.inner_html('div.enf-company-profile-info.clearfix')
                    except:
                        print("EXCEPT")
                        company_data = page2.inner_html('div.enf-company-profile-special.merging-company-profile ')

                    company_data_soup = BeautifulSoup(company_data, 'html.parser')
                    try:
                        email = company_data_soup.find('td', {'itemprop': 'email'}).find('a').text.strip()
                    except:
                        email = company_data_soup.find('div', {'itemprop': 'email'}).find('a').text.strip()

                try:
                    website = company_data_soup.find('a', {'itemprop': 'url'})['href']
                except:
                    website = all_data_soup.find('a', {'itemprop': 'url'})['href']


                try:
                    country_data = company_data_soup.find('div', {
                    'class': 'enf-company-profile-info-main pull-left'}).find('img')['alt']
                except:
                    country_data = all_data_soup.find('span', {'class': 'glyphicon glyphicon-globe'}).find_next('div').text.replace("\n", "").strip()
                    # print("TEST COUNTRY: ", country_data)
                    is_prem_acc = True

                # Work only in case with prem acc
                if is_prem_acc:
                    print("PREM ACC")
                    alternative_comp_data = all_data_soup.find('div', {'class': 'business-details'}).find_all('td')
                    # print("alter: ", alternative_comp_data)
                    title_product = [i.text.replace("\n", "").strip() for i in alternative_comp_data]
                    print(title_product)

                    minimum_order = title_product[title_product.index("Minimum Order Volume (€)") + 1]
                    print(minimum_order)
                    service_coverage = title_product[title_product.index("Service Coverage") + 1]
                    print(service_coverage)
                    language = title_product[title_product.index("Languages Spoken") + 1]

                    products = title_product[title_product.index('Languages Spoken') +2:]
                    print("Products: ", products)
                    key_value = [i for i in products if products.index(i) % 2 == 0]
                    value_dict = [i for i in products if products.index(i) % 2 == 1]
                    product_data_dict = {}
                    for j in range(len(key_value)):
                        product_data_dict.update({key_value[j]: value_dict[j]})

                    # time.sleep(1)
                    for_email = page2.inner_html('div.enf-company-profile-special.merging-company-profile ')
                    for_email_soup = BeautifulSoup(for_email, 'html.parser')
                    email = for_email_soup.find('div', {'itemprop': 'email'}).find('a').text.strip()
                    print(email)


                else:

                    # Sellers details
                    sellers_data = page2.inner_html('div.company-detail')
                    sellers_data_soup = BeautifulSoup(sellers_data, 'html.parser')

                    # dive to service section
                    try:
                        service = sellers_data_soup.find('div', {
                            'class': 'enf-section-body'}).find_all('div')
                    except:
                        service = sellers_data_soup.find('div', {
                            'class': 'business-details'}).find_all('table')
                        # print(service)

                    # Check if values are empty
                    is_empty = all_data_soup.find(
                        'div', {'class': 'company-detail'}).find('div', {'class': {'enf-section'}}).find(
                        'div', {'class': 'enf-section-body'}).find_next('div', {'class': 'enf-section-body'}).text

                    print("IS_EMPTY: ", is_empty.replace('\n', '1'))
                    print(type(is_empty))
                    if is_empty == "\n":
                        print('RRRRRRR')
                        titles_list = ['None']
                        product_list = ['None']
                        language = 'None'
                        service_coverage = "None"

                    else:

                        if right_tab is not None or right_tab_installer is not None:
                            try:
                                service_coverage = sellers_data_soup.find('div', id='seller').find(
                                    'div', class_="enf-section-body").find('div', class_="col-xs-10").text.strip()
                            except AttributeError:
                                service_coverage = service[2].text.strip()
                        else:
                            service_coverage = service[2].text.strip()

                        # scrape title product data by another element because failed to do it with css selectors or xpath
                        try:
                            products_data = sellers_data_soup.find_all('h2')[1].text
                        except IndexError:
                            products_data = sellers_data_soup.find_all('h2')[0].text
                        right_h2 = sellers_data_soup.find('h2', string=products_data).find_next()

                        if right_tab is not None and right_tab_installer is None:
                            test = sellers_data_soup.find(
                                'div', id='seller').find('a')
                            titles = test.find_parent('div').find_parent('div').find_all('div', class_="col-xs-2")
                        else:
                            titles = right_h2.find_all('div', class_='col-xs-2')

                        if right_tab_installer is not None:
                            print("right_tab_installer !!!!!!")
                            try:
                                titles = sellers_data_soup.find('div', id='seller').find_all(
                                    'div', class_='enf-section-body')[-1].find_all('div', class_="col-xs-2")
                                print(titles)
                            except AttributeError:
                                titles = right_h2.find_all('div', class_='col-xs-2')

                        # language = sellers_data_soup.find('h2', string=products_data).find_previous().text.strip()
                        try:
                            if right_tab is not None:
                                language = sellers_data_soup.find('div', id='seller').find(
                                    'div', class_="enf-section-body").find_all('div', class_="col-xs-10")[-1].text.strip()
                            else:
                                # language = sellers_data_soup.find(
                                # 'div', id='seller').find('div', class_="enf-section-body").find(
                                # 'div', class_="col-xs-10").text.strip()
                                language = sellers_data_soup.find('div', id='seller').find(
                                    'div', class_="enf-section-body").find_all('div', class_="col-xs-10")[-1].text.strip()
                        except AttributeError:
                            language = sellers_data_soup.find(
                                'div', class_='cate-content.tab-content').find_all(
                                'div', class_='enf-section-body')[0].find_all(
                                'div')[-1].find('div', class_='col-xs-10').text.strip()

                        titles_list = []
                        for title in titles:
                            titles_list.append(title.text.strip())

                        # if right_tab is not None:
                        products_raw = sellers_data_soup.find('div', id='seller').find_all('div', class_='col-xs-10')
                        products = []
                        for queue in products_raw:
                            items = queue.find_all('a')
                            item = [i.text for i in items]
                            products.append(item)
                        product_list = [", ".join(i) for i in products if i != []]

                        # Checking lists titles and products
                        if "On/Off Grid" in titles_list:
                            product_list.append("On/Off Grid")

                    # Create dictionary
                    product_data_dict = {}
                    try:
                        for j in range(len(titles_list)):
                            product_data_dict.update({titles_list[j]: product_list[j]})
                    except IndexError:
                        product_data_dict = {}
                        product_list.append(["SOWHERE ERROR!!!"])
                        for j in range(len(titles_list)):
                            product_data_dict.update({titles_list[j]: product_list[j]})
                        with open(f"data/{country_url}_ERR.txt", 'a+') as file:
                            file.writelines(link + " : ERROR in products")

                time.sleep(1)
                page2.close()

                # Data for debug
                # print(link)
                print("Company Name: ", name)
                print("Area: ", area)
                print("Distributor/Wholesaler: ", distrib)
                print("Brands Carried: ", brands)
                print("Minimum Order Volume: ", minimum_order)
                print("Products: ", products_main)
                print("Address: ", address)
                print("Phone: ", phone)
                print("Email: ", email)
                print("Website: ", website)
                print("Country: ", country_data)
                print("Service coverage: ", service_coverage)
                print("Language: ", language)
                # print("Product data: ", titles_list)
                # print("Product list: ", product_list)
                if is_prem_acc is False:
                    print("Product Dict: ", product_data_dict)
                print("-" * 30)

                goods = []
                for key, value in product_data_dict.items():
                    goods.append(key)
                    goods.append(value)
                for_write = [name, area, distrib, brands, minimum_order, products_main, address, phone, email,
                             website, country_data, service_coverage, language, ]
                for_write.extend(goods)
                with open(f"data/{country_url}.csv", "a+", encoding='utf-8', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(for_write)


                with open(f'data/{country_url}_log.txt', 'a+') as file:
                    file.writelines(link+"\n")



if __name__ == "__main__":
    country = input("Enter country: ")
    start_scrape(country)
