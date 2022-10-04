def read_log(country_data):
    with open(f"data/{country_data}_log.txt", 'r') as file:
        scrapped_urls = file.readlines()
        return [i.rstrip("\n") for i in scrapped_urls]

