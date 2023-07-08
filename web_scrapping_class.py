from bs4 import BeautifulSoup
import requests
import os
import time
import random
import json
import pandas as pd

class WebScrapping:
    urls_to_scrape = []
    new_urls = 0

    def request_n_download(self):
        # create the directory if it does not exist
        if not os.path.exists('assets'):
            os.makedirs('assets')

        urls_array = []
        with open('assets/urls.txt') as urls_file:
            for url in urls_file.readlines():
                urls_array.append(url[:-1])        
        
        print(urls_array)
        print('Se tratan de obtener nuevas URLs de la primera página de la categoría comida')
        self.new_urls = 0
        is_in_the_array = False
        url = 'https://itinerario.elonce.mx/category/comida/'
        request = requests.get(url)
        content = request.text
        is_in_the_array = self.get_urls(content, urls_array)
        print(is_in_the_array)
        page_number = 2
        time.sleep(random.randint(10, 15))
        
        print('Se tratan de obtener las URLs del resto de las páginas')
        while request.status_code != 404 and (not is_in_the_array):
            request = requests.get('https://itinerario.elonce.mx/category/comida/page/' + str(page_number) + '/')
            content = request.text
            is_in_the_array = self.get_urls(content, urls_array)
            print('Página analizada: {}'.format(page_number))
            page_number += 1
            time.sleep(random.randint(10, 15))
        
        print('Se han obtenido {} URLs nuevas'.format(self.new_urls))
        with open('assets/urls.txt', 'w') as urls_file:
            """
            Call the writelines() method on the file object 
            and pass the list of strings as an argument.
            """
            urls_file.writelines(
                # line + '\n' if i != len(self.urls_to_scrape) - 1 else line for i, line in self.urls_to_scrape)
                line + '\n' for line in self.urls_to_scrape)

    def get_urls(self, content, urls_array):
        soup = BeautifulSoup(content, 'html.parser')
        """
        Find the parent element whose children you want to extract using 
        the searching method find_all() provided by Beautiful Soup
        """
        parents = soup.findAll('h2', {'class': 'is-title post-title-alt'})
        """
        Call the findChildren() method on the parent element to extract 
        all of its children. Iterate over the children to extract the value
        of the href attribute using get() for child in children
        """
        children = [child.pop().get('href') for child in [parent.findChildren() for parent in parents]]
        for child in children:
            if child not in urls_array:
                print(children)
                self.urls_to_scrape.append(child)
                self.new_urls += 1
            else:
                return True
        return False
        
    def get_urls_data(self):
        urls_array = []
        with open('assets/urls.txt') as urls_file:
            for url in urls_file.readlines():
                urls_array.append(url[:-1])
        
        i = 0
        if self.new_urls > 0:
            print('En Progreso de obtener nuevos restaurantes de las URLs nuevas')
            for url in urls_array[:self.new_urls]: 
                request = requests.get(url)
                content = request.text
                soup = BeautifulSoup(content, 'html.parser')
                """
                You can chain these methods to navigate deeper into the HTML structure. 
                For example, result.find('div').find_all('p') will find the first <div> element 
                within the result and then find all the <p> 
                """
                p_array = soup.find('div', {'class': 'post-content description cf entry-content content-spacious'}).find_all('p')
                fig_array = soup.find('div', {'class': 'post-content description cf entry-content content-spacious'}).find_all('figure')
                dicc = {}
                dicc['nombre'] = soup.find('h1', {'class': 'is-title post-title-alt'}).get_text()
                for fig in fig_array:
                    if fig.iframe:
                        dicc['video'] = fig.iframe['src']
                for p in p_array:
                    if p.iframe:
                        dicc['video'] = p.iframe['src']
                    if 'col' in p.get_text() or '#' in p.get_text() or 'no.' in p.get_text():
                        dicc['direccion'] = p.get_text()
                        
                """
                The ensure_ascii=False parameter is used to ensure that non-ASCII characters
                are not escaped, and the encoding="utf-8" parameter is used to set the file
                encoding to UTF-8.
                """
                with open('assets/restaurantes.json', 'a', encoding="utf-8") as rest_json:
                    json.dump(dicc, rest_json, ensure_ascii=False, indent=4)
                
                i += 1
                print('Número de restaurante {}'.format(i))
                time.sleep(random.randint(10, 20))
                
                if i == 100:
                    break
        else:
            print('No hay URLs nuevas')
        print('Finalizado')
    
    def from_json_to_csv(self):
        print('Se crea un CSV a partir de un archivo JSON')
        # Load the JSON data into a pandas DataFrame
        df = pd.read_json("assets/restaurantes.json")

        # Write the DataFrame to a CSV file
        df.to_csv("assets/restaurantes.csv", index=False)