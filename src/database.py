import sqlite3
import logging

from collections import deque
logging.basicConfig(
    level=logging.INFO,
    filename='automation.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__) 

class NetworkDB:

    def __init__(self, db_path: str = "network.db") -> None:

        self.db_path = db_path # storing db's path globally
        self._conn = None #initializing self._conn as None (Null)

    def connect_db(self) -> bool: 

        try:

            self.conn = sqlite3.connect(self.db_path) # connecting to the database!
            logger.info(f"Successfully connect to {self.db_path}")

            self.conn.row_factory = sqlite3.Row # configuring row_factory from Tuples to Dictionary

            return True 
        
        except sqlite3.DatabaseError:
            
            logger.exception(f"Unable to Connect to {self.db_path}")

            return False 
        
    def fetch_all_network(self) -> deque: 

        if self.conn is None: 
            raise RuntimeError("Connection hasn't been established")
         
        try:
            
            cursor = self.conn.cursor() #creating a local cursor for fetching data
            cursor.execute("SELECT IP, port FROM networks")
            return deque((row['IP'], row['port']) for row in cursor.fetchall()) # error when column is written wrong!


        except sqlite3.Error:

            raise RuntimeError("Something went wrong")
            
            
        
    
    def add_network(self, name: str, IP: str, port: int) -> bool : 

        if self.conn is None: 
            raise RuntimeError("Connection object hasn't been created")

        try:

            #Instead of creating a local cursor, I simply executed the command through self.conn since I am not fetching data
            with self.conn:
                
                self.conn.execute("INSERT INTO networks (name, IP, port) VALUES (?, ?, ?)", (name, IP, int(port)))
                logger.info(f"Successfully added network: {name} ({IP}:{port})")
                return True 

        except sqlite3.IntegrityError:

            logger.exception("Unable to add the query", exc_info=True)

            return False


    def create_table(self) -> bool:

        if self.conn is None: 

            raise RuntimeError("Table couldn't be created since the Cursor object hasn't been created")
            
        try:
            with self.conn:
                self.conn.execute("""

                    CREATE TABLE IF NOT EXISTS networks( 
               
                            name VARCHAR(20) NOT NULL UNIQUE,
                            IP VARCHAR(15) PRIMARY KEY,
                            port INTEGER NOT NULL CHECK(port BETWEEN 0 AND 9999)
                       
                            );
                        """)
                
            return True
        except Exception as e: 

            print(f"error: {e}") 
            return False



    def close(self): 

       if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection safely closed.")

     