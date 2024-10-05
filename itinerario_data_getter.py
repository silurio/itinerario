from web_scrapping_class import WebScrapping

instanceWS = WebScrapping()
instanceWS.request_n_download()
instanceWS.get_urls_data()
instanceWS.obtener_info_restaurante()
instanceWS.generacion_masiva_urls()

# instanceWS.corrector_sitios(["La Zarza Oaxaca",
# "El Rincón de Macondo",
# "Tacos de hígado Ramírez Moranchel",
# "El Micky",
# "Café Lucky",
# "La Barra de al Lado",
# "Cacao para todos"])
# instanceWS.agregar_info_basica_restaurante([
#     {
#         "nombre": "",
#         "video": ""
#     }
# ])
# instanceWS.obtener_place_id_direccion()

instanceWS.from_json_to_csv()
# Último sitio agregado: Paletería Maya