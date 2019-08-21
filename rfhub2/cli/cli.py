import click
from pathlib import Path
from typing import Tuple

from rfhub2.cli.api_client import Client
from rfhub2.cli.rfhub_importer import RfhubImporter


@click.command()
@click.option(
    "-a",
    "--app-url",
    type=click.STRING,
    default="http://localhost:8000",
    help="Specifies IP, URI or host of rfhub2 web application. Default value is http://localhost:8000.",
)
@click.option(
    "-u",
    "--user",
    type=click.STRING,
    default="rfhub",
    help="Specifies rfhub2 user to authenticate on endpoints that requires that. Default value is rfhub.",
)
@click.option(
    "-p",
    "--password",
    type=click.STRING,
    default="rfhub",
    help="Specifies rfhub2 password to authenticate on endpoints that requires that. Default value is rfhub.",
)
@click.option(
    "--no-installed-keywords",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help="Flag specifying if package should skip loading commonly installed libraries, "
    "such as such as BuiltIn, Collections, DateTime etc.",
)
@click.option(
    "--no-db-flush",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help="Flag specifying if package should delete from rfhub2 all existing libraries.",
)
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def main(
    app_url: str,
    user: str,
    password: str,
    paths: Tuple[Path, ...],
    no_db_flush: bool,
    no_installed_keywords: bool,
) -> None:
    """Package to populate rfhub2 with robot framework keywords
       from libraries and resource files."""
    client = Client(app_url, user, password)
    rfhub_importer = RfhubImporter(client, paths, no_installed_keywords)
    if not no_db_flush:
        rfhub_importer.delete_all_collections()
    loaded_collections, loaded_keywords = rfhub_importer.import_libraries()
    print(
        f"\nSuccessfully loaded {loaded_collections} collections with {loaded_keywords} keywords."
    )
