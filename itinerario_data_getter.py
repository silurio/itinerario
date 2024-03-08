from web_scrapping_class import WebScrapping

instanceWS = WebScrapping()
instanceWS.request_n_download()
instanceWS.get_urls_data()
instanceWS.obtener_info_restaurante()
instanceWS.generacion_masiva_urls()

"""
instanceWS.corrector_sitios(["MASIOSARE", "CATFECITO", "GLACIAR", "RESTAURANTE EL PORVENIR", 
                            "CACHETADAS DON PANCHO Y DOÑA ALE", "TORTAS DE LA BARDA RENÉ", "GLACIAR: LIBROS HELADOS",
                            "BOCADIPAN", "OPPA", "GUIE' HUINI", "BIRRIOSA", "LA NEZIA CAFÉ"])
instanceWS.obtener_place_id_direccion()
"""

instanceWS.from_json_to_csv()