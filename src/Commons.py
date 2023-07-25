"""This modules contains reusable attributes and methods.
"""
from functools import wraps
import logging
import os
import pandas as pd
from pathlib import Path
import sqlite3
from urllib.parse import urlparse
import yaml


class Database:
    """SQLite Database Utility.
    Simple SQL Database to store domain information
    """

    DEFAULT_DB_FILE: str = 'logs/CertStream.db'
    DEFAULT_OUTPUT: str = 'logs/CertStream.csv'

    def __init__(self, config: dict) -> None:
        """Initialise Database with input configuration.
        Initialise Cursor and Connection too.

        Args:
            config (dict): Configuration fields.
        """
        try:
            self.database_filename: str = str(
                config['database']['filename'])
        except Exception:
            Logger.warning('Database Filename not found. '
                           f'Defaulting to {Database.DEFAULT_DB_FILE}')
            self.database_filename: str = Database.DEFAULT_DB_FILE
        FileHandler.check_availability(self.database_filename)

        try:
            self.output_filename: str = str(
                config['certstream']['output'])
        except Exception:
            Logger.warning('Output Filename not found. '
                           f'Defaulting to {Database.DEFAULT_OUTPUT}')
            self.output_filename: str = Database.DEFAULT_OUTPUT
        FileHandler.check_availability(self.output_filename)  # Early checking.

        # Build DB
        self.con: sqlite3.Connection = sqlite3.connect(self.database_filename)
        self.cur: sqlite3.Cursor = self.con.cursor()

        # Note SQLite database can accept NULL as primary keys :'(
        self.cur.execute('DROP TABLE IF EXISTS certtransp_domains')
        self.cur.execute("""CREATE TABLE certtransp_domains(
                            domain TEXT NOT NULL PRIMARY KEY)""")

    def insert(self, datalines: list[str]) -> None:
        """Insert many new values into database.

        Args:
            datalines (list[str]): Data to be added.
        """
        stmt: str = """INSERT OR REPLACE INTO certtransp_domains(domain)
                       VALUES(?)"""
        datalines = [(d,) for d in datalines]
        self.cur.executemany(stmt, datalines)
        self.con.commit()

    def execute(self, command: str) -> pd.DataFrame | None:
        """Execute SQL Command.

        Args:
            command (str): SQL Command.

        Returns:
            pd.DataFrame | None: Results of SQL Command.
        """
        try:
            if command.lower().startswith('select'):
                return pd.read_sql(command, self.con)
            else:
                self.cur.execute(command)
                self.con.commit()
        except sqlite3.ProgrammingError:
            raise sqlite3.ProgrammingError(
                'Executing more than 1 SQL statement. '
                'Please check your command!')

    def export(self) -> None:
        """Export Database to CSV.
        """
        df: pd.DataFrame = self.execute(
            'SELECT domain from certtransp_domains')
        datalines: list[str] = df['domain'].tolist()
        FileHandler.save(self.output_filename, datalines)


class FileHandler:
    """File Handling Utility.
    """

    @staticmethod
    def check_availability(filename: str) -> None:
        """Check if file is available for use.
        We can check if the file is not in use.

        Args:
            filename (str): Name of file to check.
        """
        # Create file if doesn't exist
        if not os.path.exists(filename):
            file: Path = Path(filename)
            file.parent.mkdir(parents=True, exist_ok=True)  # Make parent dirs
            file.write_text("")

        # Check 2: Check if file is closed.
        try:
            with open(filename, 'a'):
                pass
        except IOError:
            Logger.exception(IOError(f"{filename} is not available. "
                                     "Please close this file."))
            raise SystemExit()

    @staticmethod
    def read(filename: str) -> list[str]:
        """Read data from disk.

        Args:
            filename (str): Input filename.

        Returns:
            list[str]: Lines of Text from file.
        """
        FileHandler.check_availability(filename)
        with open(filename, 'r') as f:
            datalines: list[str] = f.read().splitlines()
            # Remove empty lines & whitespaces
            return [dataline.strip() for dataline in datalines if dataline]

    @staticmethod
    def save(filename: str, datalines: list[str]) -> None:
        """Write data to disk.

        Args:
            filename (str): Output filename.
            datalines (list[str]): Lines of Data to write.
        """
        FileHandler.check_availability(filename)
        with open(filename, 'a+') as f:
            f.write('\n'.join(datalines) + '\n')

    @staticmethod
    def clear(filename: str) -> None:
        """Clear data from disk.
        """
        FileHandler.check_availability(filename)
        with open(filename, 'w'):
            pass


class Logger:
    """Logging Utility.
    """

    DEFAULT_LOGFILE: str = 'logs/CertStream.log'

    def init(filename: str = DEFAULT_LOGFILE):
        """Initialise Logger.

        Args:
            filename (str): Name of log file.
                Defaults to DEFAULT_LOGIFLE.
        """
        FileHandler.check_availability(filename)  # Create /logs if needed.
        logging.basicConfig(
            filename=filename,
            level=logging.INFO,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filemode='w',
            force=True)

    init()
    LOGGER: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def log(msg: str) -> callable:
        """Decorator for logging. DO NOT EDIT WITHOUT UNDERSTANDING!
        This decorator accepts a message argument! :)

        Args:
            msg (str): Message to be logged.

        Returns:
            callable: Function with logging.
        """
        def decorator(f: callable) -> callable:
            @wraps(f)  # Helps with documentation.
            def wrapper(*args, **kwargs):
                Logger.info(f"[{f.__qualname__}] {msg}")
                return f(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def info(msg: str) -> None:
        Logger.LOGGER.info(msg)
        print(msg)

    @staticmethod
    def warning(msg: str) -> None:
        Logger.LOGGER.warning(msg)
        print(msg)

    @staticmethod
    def exception(e: Exception, msg: str = '') -> None:
        if not msg:
            msg = str(e)
        msg: str = f'{type(e).__name__}: {msg}'
        Logger.LOGGER.exception(msg)
        print(msg)

    @log('Closing Logger.')
    def __del__():
        """Terminates Logging when our logger object is destroyed.
        """
        logging.shutdown()


class Sanitiser:
    """This class sanitises domains.
    """
    def sanitise_domains(domains: list[str]) -> list[str]:
        """Removes http prefix and path suffix.
        Mere Defensive Programming.

        Args:
            domains (list[str]): Input domains to sanitise.

        Returns:
            list[str]: Sanitised domains.
        """
        sanitised: set[str] = set()
        for d in domains:
            # Proper format for urlparse
            d = f'http://{d}' if '//' not in d[:8] else d
            d = urlparse(d).netloc  # Extract domain
            d = d.removeprefix('www.').removeprefix('*.')
            sanitised.add(d)
        return list(sanitised)


class Utils:
    """Global Common Utilities.
    """

    DEFAULT_CONFIGFILE: str = 'input/config.yaml'

    @staticmethod
    def load_config(filename: str = DEFAULT_CONFIGFILE) -> dict:
        """Load configuration field from configuration file.

        Args:
            filename (str, optional): Name of Configuration File.
                Defaults to CONFIG_FILENAME.

        Returns:
            dict: Key-Value pairs of Configuration field.
        """
        FileHandler.check_availability(filename)
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
