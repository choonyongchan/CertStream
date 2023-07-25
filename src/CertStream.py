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
        config: dict = Utils.load_config()

        try:
            self.ctserver: str = str(config['certstream']['server'])
        except Exception:
            Logger.warning('CertStream Server not found. '
                           f'Defaulting to {CertStream.DEFAULT_CTSERVER}')
            self.ctserver: str = CertStream.DEFAULT_CTSERVER

        try:
            self.input: str = str(config['certstream']['input'])
        except Exception:
            Logger.warning('Regex filename not found. '
                           f'Defaulting to {CertStream.DEFAULT_INPUT}')
            self.input: str = CertStream.DEFAULT_INPUT
        FileHandler.check_availability(self.input)

        try:
            self.output: str = str(config['certstream']['output'])
        except Exception:
            Logger.warning('Output filename not found. '
                           f'Defaulting to {CertStream.DEFAULT_OUTPUT}')
            self.output: str = CertStream.DEFAULT_OUTPUT
        FileHandler.check_availability(self.output)
        FileHandler.clear(self.output)

        regexes: list[str] = FileHandler.read(self.input)
        self.pattern: re.Pattern = self.compile_regexes(regexes)
        self.database: Database = Database(config)

    @Logger.log('Compiling Regexes')
    def compile_regexes(self, regexes: list[str]) -> str:
        """This method compiles regexes into a single regex.
        """
        # Test each regex.
        if not regexes:
            Logger.exception(f'No Regexes found in {self.input}')
            raise SystemExit()
        for r in regexes:
            try:
                re.compile(r)
            except re.error:
                Logger.exception(re.error(f"Invalid Regex: {r}"))
                raise SystemExit()
        return re.compile('(?:% s)' % '|'.join(regexes))

    def is_heartbeat_msg(self, message: dict) -> bool:
        """This method checks if the message is a heartbeat message.
        """
        return message['message_type'] == 'heartbeat'

    def is_certupdate_msg(self, message: dict) -> bool:
        """This method checks if the message is a certupdate message.
        """
        return message['message_type'] == 'certificate_update'

    def is_relevant(self, domain: str) -> bool:
        """This method checks if the domain is a domain of interest.
        """
        return self.pattern.match(domain)

    def callback(self, message, context) -> None:
        """This method is called when a new CT log is recieved.
        """
        if self.is_heartbeat_msg(message):
            return
        if self.is_certupdate_msg(message):
            domains: list[str] = message['data']['leaf_cert']['all_domains']
            san_domains: list[str] = Sanitiser.sanitise_domains(domains)
            relv_domains: list[str] = [d for d in san_domains
                                       if self.is_relevant(d)]
            if not relv_domains:
                return
            for d in relv_domains:
                Logger.info(f'New Domain: {d}')
            self.database.insert(relv_domains)

    @Logger.log('Starting CertStream.')
    def start(self):
        """This method starts CertStream. Blocking code!
        """
        Logger.info('CertStream Start')
        # Blocking Code.
        certstream.listen_for_events(self.callback, url=self.ctserver)
        # Shutdown procedure
        Logger.info('Listening Stopped. Please wait for the export.')
        self.database.export()
        Logger.info('CertStream Shutdown.')
