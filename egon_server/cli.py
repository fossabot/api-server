"""The application's command line interface."""

from argparse import ArgumentParser

from flask_alembic import Alembic

from . import __version__
from .api import flask_app
from .orm import __db_version__, db


class Parser(ArgumentParser):
    """Application commandline parser

    Defines the application command line interface and handles parsing of
    command line arguments.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Define the command line interface"""

        super().__init__(*args, **kwargs)
        self.add_argument('--version', action='version', version=__version__)
        self.subparsers = self.add_subparsers(parser_class=ArgumentParser, required=True)

        migrate = self.subparsers.add_parser('migrate')
        migrate.set_defaults(action=Application.migrate_db)

        run = self.subparsers.add_parser('run')
        run.set_defaults(action=Application.run_api)
        run.add_argument('--host', type=str, default='localhost', help='the hostname to listen on')
        run.add_argument('--port', type=int, default=5000, help='the port of the webserver')
        run.add_argument('--debug', action='store_true', default=False, help='enable debug mode (insecure)')


class Application:
    """Entry point for instantiating and executing the application"""

    def __init__(self):
        """Initialize the application"""

        # This is temporary until the settings module is written
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///temp.db"
        db.init_app(flask_app)

    @staticmethod
    def migrate_db() -> None:
        """Migrate the application database to the current schema

        If the database does not exist, it is created.
        """

        with flask_app.app_context():
            alembic = Alembic(flask_app)
            alembic.upgrade(target=__db_version__)

    @staticmethod
    def run_api(host, port, debug: bool = False) -> None:
        """Run the application

        Args:
            host: the hostname to listen on
            port: the port of the webserver
            debug: Enable or disable debug mode
        """

        Application.migrate_db()
        flask_app.run(host=host, port=port, debug=debug, load_dotenv=False)

    def execute(self) -> None:
        """Parse arguments and run the application"""

        parser = Parser(
            prog='egon-server',
            description='Administrative utility for the Egon backend server')

        args = vars(parser.parse_args())
        action = args.pop('action')
        action(**args)
