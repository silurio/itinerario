from web_scrapping_class import WebScrapping

instanceWS = WebScrapping()
instanceWS.request_n_download()
instanceWS.get_urls_data()
instanceWS.obtener_info_restaurante()
instanceWS.generacion_masiva_urls()
# instanceWS.corrector_sitios(['EL MOUSTRON NARVARTE', 'SONORA STREET FOOD', 
#                             'TACOS SONOLOA', 'RESTAURANTE FRITZ', 'TAMALES EMPORIO', 'TAMALITO CORAZÓN'])
instanceWS.from_json_to_csv()