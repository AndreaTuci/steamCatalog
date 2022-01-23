import sqlite3
import time
from sqlite3 import Error
from shutil import copyfile


def db_open_conn():
    db_file = r"games_data.db"
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_tables(conn):
    sql_create_games_data_table = '''CREATE TABLE IF NOT EXISTS games_data (
                                    id integer PRIMARY KEY, 
                                    appid string NOT NULL, 
                                    name string NOT NULL,
                                    platforms string NOT NULL,
                                    genres string NOT NULL,
                                    price string NOT NULL,
                                    metacritic integer NOT NULL)'''

    sql_create_discarded_apps_table = '''CREATE TABLE IF NOT EXISTS discarded_apps (
                                    id integer PRIMARY KEY, 
                                    appid string NOT NULL)'''

    with conn:
        create_table(conn, sql_create_games_data_table)
        create_table(conn, sql_create_discarded_apps_table)


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_game_row(conn, game):
    sql = "INSERT INTO games_data(appid, name, platforms, genres, price, metacritic) VALUES(?,?,?,?,?,?)"
    cur = conn.cursor()
    cur.execute(sql, (game.appid,
                      game.name,
                      game.platforms,
                      game.genres,
                      game.price,
                      game.metacritic
                      ))
    return cur.lastrowid


def select_all_from_table(conn, table, appid):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE appid = {appid}")
    rows = cur.fetchall()
    return rows


def create_discarded_row(conn, appid):
    sql = "INSERT INTO discarded_apps(appid) VALUES(?)"
    cur = conn.cursor()
    cur.execute(sql, (appid,
                      ))
    return cur.lastrowid


def backup_db():

    # Creazione di un timestamp
    ts = time.time()

    try:
        copyfile('games_data.db', f'games_data_{ts}.db')
        print('Creata una copia di backup del db')
    except FileNotFoundError as e:
        print(e)
