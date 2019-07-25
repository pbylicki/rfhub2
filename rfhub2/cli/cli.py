import click
from typing import Tuple

from rfhub2.cli.api_client import Client
from rfhub2.cli.rfhub_importer import RfhubImporter


@click.command()
@click.option('-i', '--app-interface', type=click.STRING, default="http://0.0.0.0",
              help="Specifies IP, URI or host of rfhub2 web application. Default value is http://0.0.0.0.")
@click.option('-o', '--port', type=click.INT, default=8000,
              help="Specifies rfhub2 web application port. Default is 8000.")
@click.option('-u', '--user', type=click.STRING, default="rfhub",
              help="Specifies rfhub2 user to authenticate on endpoints that requires that. Default value is rfhub.")
@click.option('-p', '--password', type=click.STRING, default="rfhub",
              help="Specifies rfhub2 password to authenticate on endpoints that requires that. Default value is rfhub.")
@click.option('--no-installed-keywords', type=click.BOOL, default=False, is_flag=True,
              help='Flag specifying if package should skip loading commonly installed libraries, '
                   'such as such as BuiltIn, Collections, DateTime etc.')
@click.option('--no-db-flush', type=click.BOOL, default=False, is_flag=True,
              help='Flag specifying if package should delete from rfhub2 all existing libraries.')
@click.argument('--paths', nargs=-1, type=click.Path(exists=True))
def main(app_interface: str, port: str, user: str, password: str, __paths: Tuple[str, ...],
         no_db_flush: bool, no_installed_keywords: bool) -> None:
    """Package to populate rfhub2 with robot framework keywords
       from libraries and resource files."""

    client = Client(app_interface, port, user, password)
    rfhub_importer = RfhubImporter(__paths, no_installed_keywords, client)
    if not no_db_flush:
        rfhub_importer.delete_collections()
    rfhub_importer.add_collections()


if __name__ == '__main__':
    main()
