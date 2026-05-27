import sqlite3
from typing import Self

class NetworkDB:

    def __init__(self, db_path: str = "network.db") -> None:

        self._db_path = db_path # storing db's path accessible throughout the class
        self._conn = None #initializing self._conn as None (Null)
        

    def __enter__(self) -> Self:

        self.connect_db()
        self.create_table()

        return self

    def __exit__(self, exc_type, exc, tb) :
        
        self.close()

     
    def connect_db(self): 

        
        self._conn = sqlite3.connect(self._db_path, timeout=15) # connecting to the database!

        self._conn.row_factory = sqlite3.Row # configuring row_factory from Tuples to Dictionary

    
        
    def fetch_all_network(self) -> list[tuple[str, str,int]]: 

        if self._conn is None: 
            raise RuntimeError("Connection hasn't been established")
         

        cursor = self._conn.cursor() #creating a local cursor for fetching data
        cursor.execute("SELECT name, IP, port FROM networks")

        return list((row['name'],row['IP'], row['port']) for row in cursor.fetchall()) # error when column is written wrong!
            
    
    def add_network(self, name: str, IP: str, port: int): 

        if self._conn is None: 
            raise RuntimeError("Connection object hasn't been created")

        #Instead of creating a local cursor, I simply executed the command through self.conn since I am not fetching data
        with self._conn:
                
            self._conn.execute("INSERT INTO networks (name, IP, port) VALUES (?, ?, ?)", (name, IP, int(port)))

    def create_table(self):

        if self._conn is None: 

            raise RuntimeError("Table couldn't be created since the Cursor object hasn't been created")
            
        
        with self._conn:
            self._conn.execute("""

                CREATE TABLE IF NOT EXISTS networks( 
               
                        name VARCHAR(20) NOT NULL UNIQUE,
                        IP VARCHAR(15) PRIMARY KEY,
                        port INTEGER NOT NULL CHECK(port BETWEEN 0 AND 9999)
                       
                        );
                    """)

    def close(self): 

       if self._conn:
            self._conn.close()
            self._conn = None


