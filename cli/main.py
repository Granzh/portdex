import typer

from cli.backfill import backfill_app

app = typer.Typer(help="Portdex CLI")

app.add_typer(backfill_app, name="backfill")

if __name__ == "__main__":
    app()
