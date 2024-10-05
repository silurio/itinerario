from bs4 import BeautifulSoup
import requests
import os
import time
import random
import json
import sys
import pandas as pd
import googlemaps
from unidecode import unidecode

class WebScrapping:
    urls_to_scrape = []
    API_KEY = os.environ["api"]
    # API_KEY = ''
    calle = ['route', 'point_of_interest', 'establishment']


    def request_n_download(self):
        """
        Este método procesa las URLs de las nuevas recomendaciones
        de restaurantes.

        Args: Ninguno
        Returns: Ninguno
        """
        # Crea el directorio sino existe
        if not os.path.exists('assets'):
            os.makedirs('assets')

        urls_array = []
        """
        Recupera todas las URLs del archivo urls.txt, elimina el salto de línea
        y agrégalas al arreglo urls_array
        """
        with open('assets/urls.txt') as urls_file:
            for url in urls_file.readlines():
                urls_array.append(url[:-1])        
        
        print('Se tratan de obtener nuevas URLs de la primera página de la categoría comida')
        is_in_the_array = False
        url = 'https://itinerario.elonce.mx/category/comida/'
        request = requests.get(url)
        # Se recupera el contenido de la URL especificada
        content = request.text
        """
        Se agregan las nuevas URLs recuperadas a la variable global urls_to_scrape,
        si las hay. Devuelve Verdadero cuando encuentra una URL previamente
        registrada en el archivo urls.txt. Devuelve Falso si todas las URLs 
        recuperadas son nuevas
        """
        is_in_the_array = self.get_urls(content, urls_array)
        page_number = 2
        if not is_in_the_array:
            # Espera unos segundos para evitar el bloqueo por parte del sitio web de itinerario
            time.sleep(random.randint(10, 15))
        
        print('Se tratan de obtener las URLs del resto de las páginas')
        # Mientras haya páginas web disponibles y no se repitan las URLs del archivo urls.txt
        while request.status_code != 404 and (not is_in_the_array):
            request = requests.get('https://itinerario.elonce.mx/category/comida/page/' + str(page_number) + '/')
            content = request.text
            is_in_the_array = self.get_urls(content, urls_array)
            print('Página analizada: {}'.format(page_number))
            page_number += 1
            # Espera unos segundos para evitar el bloqueo por parte del sitio web de itinerario
            time.sleep(random.randint(10, 15))
        
        print('Se han obtenido {} URLs nuevas'.format(len(self.urls_to_scrape)))
        with open('assets/urls.txt', 'a') as urls_file:
            """
            Llame al método writelines() en el objeto de archivo y 
            pase la lista de cadenas como argumento.
            """
            urls_file.writelines(
                # line + '\n' if i != len(self.urls_to_scrape) - 1 else line for i, line in self.urls_to_scrape)
                line + '\n' for line in self.urls_to_scrape)


    def get_urls(self, content, urls_array):
        """
        Este método obtiene las URLs del contenido
        recuperado de las páginas de la sección de comida
        de itinerario.

        Args:
            content: El contenido recuperado de una página web.
            urls_array: El arreglo de URLs referentes a las 
            publicaciones de los restaurantes.

        Returns:
            Devuelve Verdadero cuando encuentra una URL previamente
            registrada en el archivo urls.txt.
            Devuelve Falso si todas las URLs recuperadas son nuevas
        """
        soup = BeautifulSoup(content, 'html.parser')
        """
        Encuentre el elemento principal cuyos elementos secundarios desea extraer 
        utilizando el método de búsqueda find_all() proporcionado por Beautiful Soup
        """
        parents = soup.findAll('h2', {'class': 'is-title post-title-alt'})
        """
        Llame al método findChildren() en el elemento principal para extraer todos 
        sus elementos secundarios. Iterar sobre los niños para extraer el valor del 
        atributo href usando get() para child en children
        """
        children = [child.pop().get('href') for child in [parent.findChildren() for parent in parents]]
        for child in children:
            # Si la URl obtenida no forma parte del arreglo de URLs
            if child not in urls_array:
                # Agrega la URL al arreglo de URLs a las que aplicar web scrapping
                self.urls_to_scrape.append(child)
            # Si la URL se encuentra en el arreglo de URLs
            else:
                # Detén el ciclo y devuelve Verdadero
                return True
        return False
        
        
    def get_urls_data(self):
        """
        Este método crea un objeto JSON por cada restaurante recomendado.

        Args:
        Returns:
        """
        # urls_array = []
        # with open('assets/urls.txt') as urls_file:
        #     for url in urls_file.readlines():
        #         urls_array.append(url[:-1])
        
        gmaps = googlemaps.Client(key=self.API_KEY)
        
        i = 0
        # Si hay URLs nuevas
        if len(self.urls_to_scrape) > 0:
            print('En Progreso de obtener nuevos restaurantes de las URLs nuevas')
            
            restaurantes = []
        
            # Se obtiene el arreglo de JSONs del archivo restaurantes.json
            with open('assets/restaurantes.json', 'r') as file:
                restaurantes = json.load(file)
            
            # for url in urls_array[:self.new_urls]:
            for url in self.urls_to_scrape:
                request = requests.get(url)
                content = request.text
                soup = BeautifulSoup(content, 'html.parser')
                """
                Puede encadenar estos métodos para navegar más profundamente en la
                estructura HTML. Por ejemplo, result.find('div').find_all('p') encontrará
                el primer elemento <div> dentro del resultado y luego encontrará todos los <p>
                """
                p_array = soup.find('div', {'class': 'post-content description cf entry-content content-spacious'}).find_all('p')
                fig_array = soup.find('div', {'class': 'post-content description cf entry-content content-spacious'}).find_all('figure')
                dicc = {}
                # Se obtiene el nombre del restaurante, ubicando el elemento HTML h1 con la class especificada
                dicc['nombre'] = soup.find('h1', {'class': 'is-title post-title-alt'}).get_text()
                
                elemento_registrado = False
                # Se busca el sitio, por nombre, en el arreglo de restaurantes
                for dict in restaurantes:
                    if dict.get("nombre") == dicc['nombre']:
                        elemento_registrado = True
                        break
                
                # Si el sitio ya existe, salta a la siguiente URL
                if elemento_registrado:
                    continue
                
                # Busca el sitio en Google Maps por nombre
                sitio = gmaps.find_place(input=sitio['nombre'], input_type='textquery')
                
                # print(sitio)
                
                # Obtiene los posibles place IDs, de Google Maps, del sitio
                sitios = [candidate['place_id'] for candidate in sitio['candidates']]
                # Si existe un sólo ID para el sitio
                if len(sitios) == 1:
                    # Saca el ID del arreglo y lo coloca en la propiedad gmaps_id
                    id = sitios.pop()
                    dicc['gmaps_id'] = id
                else:
                    # Agrega el arreglo de IDs a la propiedad gmaps_id
                    dicc['gmaps_id'] = sitios
                    
                # Por cada elemento HTML figure
                for fig in fig_array:
                    # Si el elemento hijo iframe existe en figure 
                    if fig.iframe:
                        # Obten el enlace de video de la propiedad src del elemento iframe
                        dicc['video'] = fig.iframe['src']
                # Por cada elemento HTML p
                for p in p_array:
                    # Si el elemento hijo iframe existe en p 
                    if p.iframe:
                        # Obten el enlace de video de la propiedad src del elemento iframe
                        dicc['video'] = p.iframe['src']
                    # Si elemento p tiene una string con las substrings col, # o no.
                    if 'col' in p.get_text() or '#' in p.get_text() or 'no.' in p.get_text():
                        #Guarda la string en la propiedad direccion del diccionario
                        dicc['direccion'] = p.get_text()
                       
                """
                Se obtiene el arreglo de JSONs del archivo restaurantes.json, se agrega
                el objeto JSON del restaurante en cuestión al arreglo
                """ 
                data = []
                with open('assets/restaurantes.json', 'r') as file:
                    data = json.load(file)
                data.append(dicc)
                """
                Añade todo el arreglo de objetos JSON de los restaurantes, incluido el 
                restaurante recién añadido, al archivo de restaurantes.json. 
                El parámetro sure_ascii=False se usa para garantizar que no se escapen los 
                caracteres que no son ASCII, y el parámetro encoding="utf-8" se usa para 
                establecer la codificación del archivo en UTF-8. El parámetro indent para
                formatear el JSON en cuestión
                """
                with open('assets/restaurantes.json', 'w', encoding="utf-8") as rest_json:
                    json.dump(data, rest_json, ensure_ascii=False, indent=4)
                
                i += 1
                # Va indicando cuantas URLs de restaurantes se han procesado
                print('Número de restaurante {}'.format(i))
                # Espera unos segundos para evitar el bloqueo por parte del sitio web de itinerario
                time.sleep(random.randint(10, 20))
                """
                Cuando se hayan procesado 100 URLs detén el método para evitar el bloqueo
                por parte del sitio web de itinerario
                """
                if i == 100:
                    break
            print('Finalizado')
            return True
        else:
            print('No hay URLs nuevas')
            print('Finalizado')
            return False
        
    
    def from_json_to_csv(self):
        """
        Este método genera un archivo CSV a partir del archivo restaurantes.json

        Args:
        Returns:
        """
        print('Se crea un CSV a partir de un archivo JSON')
        # Cargue los datos JSON en un DataFrame de pandas
        df = pd.read_json("assets/restaurantes.json")
        
        # Retira la columna 'gmaps_id'
        df = df.drop(['gmaps_id', 'lat', 'lng'], axis=1)
        
        # Renombrando columnas para el CSV    
        df = df.rename(columns={
            'video': 'recomendacion de itinerario',
            'enlace_google_maps': 'enlace al sitio en google maps'
        })

        # Escribir el DataFrame en un archivo CSV
        df.to_csv("assets/restaurantes.csv", index=False)
        
        
    def obtener_info_restaurante(self):
        """
        Este método verifica y registra el estado de los restaurantes: 
        Cerrado permanentemente, temporalmente y Abierto.
        También obtiene las coordenadas de los mismos.
        Verifica si la dirección de Itinerario coincide con la de Maps

        Args:
        Returns:
        """
        restaurantes = []
        restaurantes_place_ids_caducos = []
        restaurantes_direcciones_diferentes = []
        gmaps = googlemaps.Client(key=self.API_KEY)
        
        # Se obtiene el arreglo de JSONs del archivo restaurantes.json
        with open('assets/restaurantes.json', 'r') as file:
            restaurantes = json.load(file)
        
        # Se repasa el arreglo de restaurantes
        for sitio in restaurantes:
            # Si el restaurante tiene un sólo place_id
            esString = isinstance(sitio['gmaps_id'], str)
            
            if sitio['gmaps_id'] != "" and esString:

                try:
                    detalles_sitio = gmaps.place(place_id=sitio['gmaps_id'])
                    # business_status = detalles_sitio['result']['business_status']
                    business_status = detalles_sitio

                    # Si el valor obtenido es un diccionario y tiene la propiedad result
                    if 'result' in business_status:
                        # Si el valor obtenido es un diccionario y tiene la propiedad business_status
                        if 'business_status' in business_status['result']:
                            if business_status['result']['business_status'] == 'CLOSED_PERMANENTLY':
                                sitio['estado'] = 'Cerrado permanentemente'
                            elif business_status['result']['business_status'] == 'CLOSED_TEMPORARILY':
                                sitio['estado'] = 'Cerrado temporalmente'
                            else:
                                sitio['estado'] = 'En operaciones'
                        
                        # Para la carga masiva de coordenadas
                        if 'geometry' in business_status['result']:
                            if 'location' in business_status['result']['geometry']:
                                coordenadas = business_status['result']['geometry']['location']
                                sitio['lat'] = coordenadas['lat']
                                sitio['lng'] = coordenadas['lng']
                                
                            # print(sitio['estado'])
                        
                        # Verifica si la dirección registrada coincide con la del sitio localizado en Maps
                        if 'address_components' in business_status['result'] and sitio['estado'] != 'Cerrado permanentemente':
                            try:
                                dicc_encontrado = [dicc for dicc in business_status['result']['address_components']
                                                if any(valor in dicc['types'] for valor in self.calle)].pop()
                                
                                address = unidecode(sitio['direccion'].lower())
                                
                                if unidecode(dicc_encontrado['long_name'].lower()) in address or \
                                    unidecode(dicc_encontrado['short_name'].lower()) in address:
                                    pass
                                else:
                                    print("El sitio {} tiene una dirección distinta".format(sitio['nombre']))
                                    restaurantes_direcciones_diferentes.append(sitio['nombre'] + ': ' + sitio['direccion'])
                                    restaurantes_direcciones_diferentes.append(dicc_encontrado['long_name'] + ', '
                                                                            + dicc_encontrado['short_name'])   
                            except:
                                # print(business_status['result']['address_components'])
                                print(f"An error occurred: {sys.exc_info()}")                           
                            
                    # print(sitio)
                except:
                    print("El sitio {} tiene un place ID caduco".format(sitio['nombre']))
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    print(f"An error occurred with place ID: {exc_type.__name__}: {exc_value}")
                    restaurantes_place_ids_caducos.append(sitio['nombre'])
                
            # Si el restaurante tiene varios place_id
            elif not esString:
                print("El sitio {} debe revisarse".format(sitio['nombre']))
                sitio['lat'] = 0
                sitio['lng'] = 0
        
        # Almacena los restaurantes con place IDs caducos en un archivo de texto, el cual
        # se sobrescribirá en la sig. ejecución 
        if len(restaurantes_place_ids_caducos) > 0:
            with open('assets/place_ids_caducos.txt', 'w', encoding="utf-8") as caducos:
                caducos.writelines(line + '\n' for line in restaurantes_place_ids_caducos)
        else:
            with open('assets/place_ids_caducos.txt', 'w'):
                pass
        
        # Almacena los restaurantes con direcciones distintas, entre la de Itinerario y Maps,
        # en un archivo de texto, el cual se sobrescribirá en la sig. ejecución
        if len(restaurantes_direcciones_diferentes) > 0:
            with open('assets/direcciones_distintas.txt', 'w', encoding="utf-8") as distintas:
                distintas.writelines(line + "\n\n" if i % 2 == 1 else line + "\n" 
                                     for i, line in enumerate(restaurantes_direcciones_diferentes))
        else:
            with open('assets/direcciones_distintas.txt', 'w'):
                pass
        
        # Almacena el estado actualizado de todos los restaurantes en el archivo restaurantes.json
        with open('assets/restaurantes.json', 'w', encoding="utf-8") as rest_json:
            json.dump(restaurantes, rest_json, ensure_ascii=False, indent=4)        
        
    
    def generacion_masiva_urls(self):
        """
        Este método genera URLs en Google Maps para todos los
        restaurantes usando el place ID

        Args:
        Returns:
        """
        with open('assets/restaurantes.json', 'r') as file:
            restaurantes = json.load(file)
            
        for sitio in restaurantes:
            if sitio['gmaps_id'] != "":
                sitio['enlace_google_maps'] = ('https://www.google.com/maps/search/?api=1&query=' +
                                                str(sitio['lat']) + '%2C' + str(sitio['lng']) + 
                                                '&query_place_id=' + sitio['gmaps_id'])
            else:
                sitio['enlace_google_maps'] = ""
                
        with open('assets/restaurantes.json', 'w', encoding="utf-8") as rest_json:
            json.dump(restaurantes, rest_json, ensure_ascii=False, indent=4) 
            
            
    def agregar_coordenadas_estado_url(self, sitio):
        """
        Este método corrige coordenadas, estado
        y URL de un sitio dado. También verifica si la 
        dirección de Itinerario coincide con la de Maps

        Args: 
            sitio: Restaurante a actualizar
        Returns:
        """
        gmaps = googlemaps.Client(key=self.API_KEY)

        # Si el restaurante tiene un sólo place_id
        esString = isinstance(sitio['gmaps_id'], str)
        if sitio['gmaps_id'] != "" and esString:

            detalles_sitio = gmaps.place(place_id=sitio['gmaps_id'])
            # business_status = detalles_sitio['result']['business_status']
            business_status = detalles_sitio

            # print(business_status)
            # Si el valor obtenido es un diccionario y tiene la propiedad result
            if 'result' in business_status:
                
                # Si el valor obtenido es un diccionario y tiene la propiedad business_status
                if 'business_status' in business_status['result']:
                    if business_status['result']['business_status'] == 'CLOSED_PERMANENTLY':
                        sitio['estado'] = 'Cerrado permanentemente'
                    elif business_status['result']['business_status'] == 'CLOSED_TEMPORARILY':
                        sitio['estado'] = 'Cerrado temporalmente'
                    else:
                        sitio['estado'] = 'En operaciones'
                
                # Para la carga masiva de coordenadas
                if 'geometry' in business_status['result']:
                    if 'location' in business_status['result']['geometry']:
                        coordenadas = business_status['result']['geometry']['location']
                        sitio['lat'] = coordenadas['lat']
                        sitio['lng'] = coordenadas['lng']
                        
                        sitio['enlace_google_maps'] = ('https://www.google.com/maps/search/?api=1&query=' +
                                                str(sitio['lat']) + '%2C' + str(sitio['lng']) + 
                                                '&query_place_id=' + sitio['gmaps_id'])        
                else:
                    sitio['enlace_google_maps'] = ""
                    
                if 'address_components' in business_status['result']:
                    if sitio['direccion'] == '':
                        sitio['direccion'] = business_status['result']['formatted_address']
                    else :  
                        try:
                            dicc_encontrado = [dicc for dicc in business_status['result']['address_components']
                                            if any(valor in dicc['types'] for valor in self.calle)].pop()
                            
                            address = unidecode(sitio['direccion'].lower())
                            print(address)
                            print(unidecode(dicc_encontrado['long_name'].lower()))
                            print(unidecode(dicc_encontrado['short_name'].lower()))
                                
                            if unidecode(dicc_encontrado['long_name'].lower()) in address or \
                                unidecode(dicc_encontrado['short_name'].lower()) in address:
                                pass
                            else:
                                print("El sitio {} tiene una dirección distinta".format(sitio['nombre']) + "\n\n")
                        except:
                            print("El sitio {} tiene problema con los componentes de la dirección".format(sitio['nombre']))
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            print(f"An error occurred with address_components: {exc_type.__name__}: {exc_value}")

        # Si el restaurante tiene varios place_id
        elif not esString:
            print("El sitio {} debe revisarse".format(sitio['nombre']))
            sitio['lat'] = 0
            sitio['lng'] = 0
            sitio['enlace_google_maps'] = ""
            

    def corrector_sitios(self, sitios):
        """
        Este método corrige coordenadas, estado
        y URL de un sitio individual

        Args: 
            nombre_sitio: Nombre del sitio a corregir
        Returns:
        """
        
        restaurantes = []
        
        # Se obtiene el arreglo de JSONs del archivo restaurantes.json
        with open('assets/restaurantes.json', 'r') as file:
            restaurantes = json.load(file)
        
        corregidos = 0
        for nombre_sitio in sitios:
            sitio = {}
            # Se busca el sitio, por nombre, en el arreglo de diccionarios
            for dict in restaurantes:
                if dict.get("nombre") == nombre_sitio:
                    sitio = dict
                    restaurantes.remove(dict)
                    print('Sitio encontrado')
                    break

            if sitio:
                
                self.agregar_coordenadas_estado_url(sitio)
                restaurantes.append(sitio)
                corregidos += 1 

            else:
                print('Sitio no encontrado')
        
        if corregidos > 0:
            # Almacena el estado actualizado de todos los restaurantes en el archivo restaurantes.json
            with open('assets/restaurantes.json', 'w', encoding="utf-8") as rest_json:
                json.dump(restaurantes, rest_json, ensure_ascii=False, indent=4) 

         
    def obtener_place_id_direccion(self):
        """
        Este método obtiene la información restante de un sitio
        que sólo tiene su nombre y la URL de recomendación

        Args: 
        Returns:
        """
        restaurantes = []
        
        # Se obtiene el arreglo de JSONs del archivo restaurantes.json
        with open('assets/restaurantes.json', 'r') as file:
            restaurantes = json.load(file)
        
        gmaps = googlemaps.Client(key=self.API_KEY)
        
        restaurantes_por_actualizar = []
        # Se busca el sitio, por nombre, en el arreglo de diccionarios
        for dict in restaurantes:
            if dict.get("direccion") == "":
                restaurantes_por_actualizar.append(dict)
                restaurantes.remove(dict)

        if len(restaurantes_por_actualizar) > 0:
            for sitio in restaurantes_por_actualizar:
                # Busca el sitio en Google Maps por nombre
                if sitio['gmaps_id'] == "":
                    rest = gmaps.find_place(input=sitio['nombre'], input_type='textquery')
                    
                    print(sitio['nombre'])
                    
                    # Obtiene los posibles place IDs, de Google Maps, del sitio
                    places_ids = [candidate['place_id'] for candidate in rest['candidates']]
                    # Si existe un sólo ID para el sitio
                    if len(places_ids) == 1:
                        # Saca el ID del arreglo y lo coloca en la propiedad gmaps_id
                        id = places_ids.pop()
                        detalles = gmaps.place(place_id=id, fields=['formatted_address'])
                        sitio['gmaps_id'] = id
                        sitio['direccion'] = detalles['result']['formatted_address']
                        self.agregar_coordenadas_estado_url(sitio)
                    else:
                        # Agrega el arreglo de IDs a la propiedad gmaps_id
                        sitio['gmaps_id'] = places_ids
                else:
                    detalles = gmaps.place(place_id=sitio['gmaps_id'], fields=['formatted_address'])
                    sitio['direccion'] = detalles['result']['formatted_address']
                    self.agregar_coordenadas_estado_url(sitio)
            
            todos = restaurantes + restaurantes_por_actualizar
            
            with open('assets/restaurantes.json', 'w', encoding="utf-8") as rest_json:
                    json.dump(todos, rest_json, ensure_ascii=False, indent=4) 
                    
    
    def agregar_info_basica_restaurante(self, sitios_nuevos):
        """
        Este método agrega un restaurante con la información
        básica proporcionada: su nombre y URL de recomendación
        """
        restaurantes = []
        
        # Se obtiene el arreglo de JSONs del archivo restaurantes.json
        with open('assets/restaurantes.json', 'r') as file:
            restaurantes = json.load(file)
            
        for sitio in sitios_nuevos:
            sitio.update({
                "direccion": "",
                "gmaps_id": "",
                "estado": "",
                "enlace_google_maps": "",
                "lat": 0,
                "lng": 0
            })
            restaurantes.append(sitio)
                    
        with open('assets/restaurantes.json', 'w', encoding="utf-8") as rest_json:
                    json.dump(restaurantes, rest_json, ensure_ascii=False, indent=4)