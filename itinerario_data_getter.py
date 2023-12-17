from web_scrapping_class import WebScrapping

instanceWS = WebScrapping()
instanceWS.request_n_download()
instanceWS.get_urls_data()
instanceWS.obtener_info_restaurante()
instanceWS.generacion_masiva_urls()

# instanceWS.corrector_sitios(["SOPES DE LA OBRERA", "PARRILLADA Y PIZZERIA URUGUAYA QUE ASADO", "COREANA CHICKEN", "ENAK INDONESIAN RESTAURANT(BY ANGEL'S KITCHEN)", "TALLER DE PASTELES", "NIGHTMARES"])
# instanceWS.obtener_place_id_direccion()

instanceWS.from_json_to_csv()