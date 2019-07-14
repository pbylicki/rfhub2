import click
from rfhub2.cli.population import LibraryPopulation


@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('--no-installed-keywords', 'no_installed_keywords', default=False,
              help='do not load some common installed keyword libraries, such as BuiltIn.')
def main(paths, no_installed_keywords):
    """Package to populate rfhub2 with libraries and resource documentation"""

    library = LibraryPopulation(paths, no_installed_keywords)
    library.add_collections()


if __name__ == '__main__':
    main()
