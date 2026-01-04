"""Typer CLI entrypoint fixture."""
import typer

app = typer.Typer()


def helper():
    """Helper function called by CLI commands."""
    return "processed"


@app.command()
def main(name: str = "world"):
    """Main CLI command - should be detected as entrypoint."""
    result = helper()
    typer.echo(f"Hello {name}: {result}")


@app.command()
def greet(name: str):
    """Greet command - should be detected as entrypoint."""
    helper()
    typer.echo(f"Greetings, {name}!")


@app.callback()
def callback():
    """Callback - should be detected as entrypoint."""
    pass


if __name__ == "__main__":
    app()
