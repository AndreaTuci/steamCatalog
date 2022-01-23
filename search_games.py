import requests
from config import DB
# Controlla sul file config quale tipo di db si è scelto di usare
if DB == 'sqlite3':
    from db_ops_sqlite import *
else:
    from db_ops_postgres import *


# Creo la classe Game per salvare le informazioni che mi servono su ogni gioco
class Game:
    appid = ''
    name = ''
    platforms = ''
    genres = ''
    price = ''
    metacritic = 0

    # Quando viene inizializzata deve ricevere appid e nome in una lista
    def __init__(self, base_info):
        self.appid = base_info[0]
        self.name = base_info[1]


def obtain_games(response):
    while True:
        print('Sto cercando di ottenere la lista completa da Steam...')
        if response.status_code == 200:
            # Se lo status è 200 otteniamo il json con tutti i dati
            res = response.json()
            # Prendiamo quello che ci serve (appid, name)
            apps = res['applist']['apps']
            print(f'Ricevuti {len(apps)} elementi')
            break
    return apps


def add_to_catalog(apps, conn):
    while True:

        # Tramite input decidiamo quanti elementi valutare

        limit = input('Quante app vuoi valutare? ')
        try:
            int(limit)
            break
        except ValueError as e:
            print(e)

    limit = int(limit)

    count = 0
    for app in apps:
        if count < limit:
            try:
                appdid = app['appid']
                # Bitwise, controllo se la app è nei giochi salvati o nelle app scartate
                if bool(select_all_from_table(conn, 'games_data', appdid)) | bool(
                        select_all_from_table(conn, 'discarded_apps', appdid)):
                    print('Già presente')
                else:
                    response = requests.get(fr'https://store.steampowered.com/api/appdetails?appids={appdid}')
                    print('-'*30)
                    if response.status_code == 200:
                        res = response.json()
                        count += 1
                        print(f'Valutate {count} app')

                        # Se il db è sqlite3 salviamo una copia backup ogni 5000 elementi
                        if DB == 'sqlite3' and count % 5000 == 0:
                            backup_db()
                        try:
                            is_game = res[f'{appdid}']['data']['type']

                            # Se l'app considerata è un gioco andiamo avanti, altrimenti si scarta
                            if is_game == 'game':
                                print('Nuovo')
                                game = Game([str(appdid), app['name']])

                                # Piattaforme
                                platforms = ''
                                for platform in res[f'{appdid}']['data']['platforms']:
                                    if res[f'{appdid}']['data']['platforms'][platform]:
                                        platforms = platforms + platform + ', '

                                # __setattr__ è un metodo che riceve il nome dell'attributo da cambiare
                                # e il nuovo valore che gli vogliamo assegnare
                                game.__setattr__('platforms', platforms)

                                # Prezzo
                                # try ed except sono necessari perché a volte le chiavi mancano nella risposta
                                try:
                                    print(res[f'{appdid}']['data']['price_overview']['final_formatted'])
                                    price = res[f'{appdid}']['data']['price_overview']['final_formatted']
                                except KeyError:
                                    print('Free-to-play')
                                    price = 'Free-to-play'
                                game.__setattr__('price', price)

                                # Generi
                                genres = ''
                                for genre in res[f'{appdid}']['data']['genres']:
                                    genres = genres + genre['description'] + ', '
                                game.__setattr__('genres', genres)

                                # Punteggio Metacritic
                                try:
                                    metacritic = res[f'{appdid}']['data']['metacritic']['score']
                                except KeyError:
                                    metacritic = 0
                                game.__setattr__('metacritic', metacritic)

                                # Raccolti i dati nell'oggetto Game lo passo alla funzione che li salva
                                create_game_row(conn, game)

                            else:
                                create_discarded_row(conn, str(appdid))
                                print(f'Scartato: {is_game}')

                        except KeyError as e:
                            create_discarded_row(conn, str(appdid))
                            print(f'{e}: chiave inesistente')

            except Exception as e:
                print(e)
                count += 1
