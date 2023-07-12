from web_scrapping_class import WebScrapping

instanceWS = WebScrapping()
instanceWS.request_n_download()
continuar = instanceWS.get_urls_data()
if continuar:
    instanceWS.from_json_to_csv()