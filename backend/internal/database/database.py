from mysql.connector import connect, Error
from mysql.connector.abstracts import MySQLConnectionAbstract
import logging as log

class db_conn:
    connection: MySQLConnectionAbstract

    def connect(self, host: str, port: int, username: str, password: str, database: str):
        try:
            conn = connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
        except Error as err:
            log.error(f"can't estabilished connection with database: {err}")
        else:
            if isinstance(conn, MySQLConnectionAbstract):
                self.connection = conn
                return
            else:
                log.error("internal erorr: database connection type mismatch")
                return
