import click

import alqtendpy.compileui


@click.command()
@click.option(
    '--ui',
    'ui_paths',
    multiple=True, type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    '--directory',
    '--dir',
    'directories',
    default=['.'],
    multiple=True,
    type=click.Path(exists=True, file_okay=False),
)
@click.option('--suffix', default='_ui')
@click.option('--encoding', default='utf-8')
def cli(ui_paths, directories, suffix, encoding):
    alqtendpy.compileui.compile_ui(
        file_paths=ui_paths,
        directory_paths=directories,
        extension='.ui',
        suffix=suffix,
        encoding=encoding,
        output=click.echo,
    )
