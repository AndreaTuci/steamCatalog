import psycopg2

# I dati per la connessione vengono importati dal file postgres_setup.py
# che non deve essere messo sul repo per ragioni di sicurezza

# host = "localhost",
# database = "nome-del-database",
# user = "nome-utente",
# password = "password"

from postgres_setup import *


def db_open_conn():
    conn = None
    try:
        conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password)
    except (Exception, psycopg2.DatabaseError) as e:
        print(e)
    return conn


def create_tables(conn):
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS games_data (
            id SERIAL PRIMARY KEY,
            appid VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            platforms VARCHAR(255) NOT NULL,
            genres VARCHAR(255) NOT NULL,
            price VARCHAR(255) NOT NULL,
            metacritic INTEGER NOT NULL
        )""",
        '''CREATE TABLE IF NOT EXISTS discarded_apps (
        id SERIAL PRIMARY KEY, 
        appid VARCHAR(255) NOT NULL)'''
    )

    cur = conn.cursor()

    # Crea le tabelle una alla volta
    for command in commands:
        cur.execute(command)

    # Chiude la comunicazione con il database PostgreSQL
    cur.close()

    # Commit dei cambiamenti
    conn.commit()


def create_game_row(conn, game):
    sql = """INSERT INTO games_data(appid, name, platforms, genres, price, metacritic)
            VALUES(%s,%s,%s,%s,%s,%s) RETURNING id;"""
    cur = conn.cursor()
    db_id = None
    try:
        cur.execute(sql, (game.appid,
                          game.name,
                          game.platforms,
                          game.genres,
                          game.price,
                          game.metacritic
                          ))

        # Restituisce l'id appena generato
        db_id = cur.fetchone()[0]
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    cur.close()

    return db_id


def create_discarded_row(conn, appid):
    sql = "INSERT INTO discarded_apps(appid) VALUES(%s) RETURNING id"
    cur = conn.cursor()
    db_id = None
    try:
        cur.execute(sql, (appid,
                          ))
        db_id = cur.fetchone()[0]
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    cur.close()

    return db_id


def select_all_from_table(conn, table, appid):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE appid = Cast({appid} As varchar)")
    rows = cur.fetchall()
    cur.close()
    return rows


def close_conn(conn):
    conn.close()
