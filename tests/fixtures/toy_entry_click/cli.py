"""Click CLI entrypoint fixture."""
import click


def helper():
    """Helper function called by CLI commands."""
    return "processed"


@click.command()
def main():
    """Main CLI command - should be detected as entrypoint."""
    result = helper()
    click.echo(result)


@click.group()
def cli():
    """CLI group - should be detected as entrypoint."""
    pass


@cli.command()
def sub_command():
    """Subcommand - should be detected as entrypoint."""
    helper()


if __name__ == "__main__":
    main()
