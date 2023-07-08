from bs4 import BeautifulSoup
import requests
import os
import time
import random
import json
import pandas as pd

class WebScrapping:
    urls_to_scrape = []

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
        
        i = 0
        # Si hay URLs nuevas
        if len(self.urls_to_scrape) > 0:
            print('En Progreso de obtener nuevos restaurantes de las URLs nuevas')
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
                Añade el diccionario de un restaurante como un objeto JSON en el archivo
                restaurantes.json. 
                El parámetro sure_ascii=False se usa para garantizar que no se escapen los 
                caracteres que no son ASCII, y el parámetro encoding="utf-8" se usa para 
                establecer la codificación del archivo en UTF-8. El parámetro indent para
                formatear el JSON en cuestión
                """
                with open('assets/restaurantes.json', 'a', encoding="utf-8") as rest_json:
                    json.dump(dicc, rest_json, ensure_ascii=False, indent=4)
                
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
        else:
            print('No hay URLs nuevas')
        print('Finalizado')
    
    def from_json_to_csv(self):
        """
        Este método genera un archivo CSV a partir del archivo restaurantes.json

        Args:
        Returns:
        """
        print('Se crea un CSV a partir de un archivo JSON')
        # Cargue los datos JSON en un DataFrame de pandas
        df = pd.read_json("assets/restaurantes.json")

        # Escribir el DataFrame en un archivo CSV
        df.to_csv("assets/restaurantes.csv", index=False)