"""This module starts CertStream, a background program.
CertStream continuously monitors Certificate Transparency logs for newly
registered domains. If the newly registered domain is a domain of intereest,
the domain will be logged.
"""
import certstream
import re

from src.Commons import Database, FileHandler, Logger, Sanitiser, Utils


class CertStream:

    DEFAULT_CTSERVER: str = 'wss://certstream.calidog.io'
    DEFAULT_INPUT: str = 'input/input_regex.txt'
    DEFAULT_OUTPUT: str = 'logs/certstream.txt'

    @Logger.log('Initialising CertStream')
    def __init__(self):
        """Initialise CertStream.
        """
        def read_ctserver() -> str:
            try:
                ctserver: str = str(config['certstream']['server'])
            except Exception:
                Logger.warning('CertStream Server not found. '
                               f'Defaulting to {CertStream.DEFAULT_CTSERVER}')
                ctserver: str = CertStream.DEFAULT_CTSERVER
            return ctserver

        def read_output() -> str:
            try:
                output: str = str(config['certstream']['output'])
            except Exception:
                Logger.warning('Output filename not found. '
                               f'Defaulting to {CertStream.DEFAULT_OUTPUT}')
                output: str = CertStream.DEFAULT_OUTPUT
            finally:
                FileHandler.check_availability(output)
                FileHandler.clear(output)
            return output

        def read_regex() -> re.Pattern:

            def compile_regexes(regexes: list[str]) -> str:
                """Compile list of regexes into a single regex,
                such that the regex matches if any of the regexes match.

                Args:
                    regexes (list[str]): List of input regexes

                Returns:
                    str: Compiled combined regex.
                """
                # Test each regex.
                for r in regexes:
                    try:
                        re.compile(r)
                    except re.error:
                        Logger.exception(re.error(f"Invalid Regex: {r}"))
                        raise SystemExit()

                regex: str = '(?:% s)' % '|'.join(regexes)
                return re.compile(regex)

            try:
                input: str = str(config['certstream']['input'])
            except Exception:
                Logger.warning('Regex filename not found. '
                               f'Defaulting to {CertStream.DEFAULT_INPUT}')
                input: str = CertStream.DEFAULT_INPUT
            finally:
                FileHandler.check_availability(input)

            regexes: list[str] = FileHandler.read(input)
            if not regexes:
                Logger.exception(f'No Regexes found in {input}')
                raise SystemExit()
            return compile_regexes(regexes)

        config: dict = Utils.load_config()
        self.ctserver: str = read_ctserver()
        self.output: str = read_output()
        self.pattern: re.Pattern = read_regex()
        self.database: Database = Database(config)

    def is_certupdate_msg(self, message: dict) -> bool:
        """Checks if the message is a certupdate message.

        Args:
            message (dict): Message from a CT log.

        Returns:
            bool: True if message is a certupdate message.
        """
        return message['message_type'] == 'certificate_update'

    def is_relevant(self, domain: str) -> bool:
        """Checks if the domain matches the regex.

        Args:
            domain (str): Domain to check.

        Returns:
            bool: True if domain matches the regex.
        """
        return self.pattern.match(domain)

    def callback(self, message: dict, context: dict) -> None:
        """Callback function for CertStream. Called when a new CT log is
        received.

        Args:
            message (dict): Message from a CT log.
            context (dict): Context from a CT log.
        """
        if self.is_certupdate_msg(message):
            domains: list[str] = message['data']['leaf_cert']['all_domains']
            san_domains: list[str] = Sanitiser.sanitise_domains(domains)
            relv_domains: list[str] = [d for d in san_domains
                                       if self.is_relevant(d)]
            if relv_domains:
                for d in relv_domains:
                    Logger.info(f'New Domain: {d}')
                self.database.insert(relv_domains)

    @Logger.log('Starting CertStream.')
    def start(self) -> None:
        """This method starts CertStream. Blocking code!
        """
        # Blocking Code.
        certstream.listen_for_events(self.callback, url=self.ctserver)
        # Shutdown procedure
        Logger.info('Listening Stopped. Please wait for the export.')
        self.database.export()
        Logger.info('CertStream Shutdown.')
