from typing import Tuple
import click
from rfhub2.cli.population import AppPopulation


@click.command()
@click.option('-i', '--app-interface', type=click.STRING, default="0.0.0.0",
              help="Specifies IP, URI or host of rfhub2 web application. Default value is 0.0.0.0.")
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

    populate_app = AppPopulation(app_interface, port, user, password, __paths, no_installed_keywords)
    if not no_db_flush:
        populate_app.delete_collections()
    populate_app.add_collections()


if __name__ == '__main__':
    main()
