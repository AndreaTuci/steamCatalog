from search_games import *
from config import DB
import requests

# Le librerie necessarie si installano con 'pip install -r requirements.txt'

if __name__ == '__main__':

    # url per ottenere la lista completa da Steam
    url = r"http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json"

    # Risposta dal server
    response = requests.get(url)

    while True:
        search_games = input('Vuoi aggiungere giochi al catalogo? (s/n) ').lower()
        if search_games in ['s', 'n']:
            break

    if search_games == 's':

        if DB == 'sqlite3':
            # Se si usa sqlite3 fa un backup del db prima di iniziare a lavorarci. Al nome aggiungo ts
            backup_db()

        # Operazioni preliminari per la gestione del db
        # Creo la connessione e se non esistono le tabelle
        conn = db_open_conn()
        create_tables(conn)

        # Prendo la lista di tutte le app
        apps = obtain_games(response)

        # Avvio la catalogazione
        add_to_catalog(apps, conn)

        # Finito il lavoro chiudo la connessione con il db
        conn.close()
