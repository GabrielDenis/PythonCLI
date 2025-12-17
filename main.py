import typer
import db
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def add(name: str):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO topics (name, status) VALUES (%s, %s)", (name, "todo"))
    conn.commit()
    cur.close()
    conn.close()

    print(f"Topic '{name}' added successfully.")

@app.command()
def list():
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM topics")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    table = Table(title="My Learning Roadmap")
    table.add_column("Name", justify='Left', style='cyan')
    table.add_column("Status", justify='Left', style='magenta')

    for row in rows:
        table.add_row(row[1], row[2])

    console.print(table)

@app.command()
def done(name: str):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE topics SET status = 'done' WHERE name = %s", (name,))
    conn.commit()
    cur.close()
    conn.close()

    print(f"Topic '{name}' marked as done successfully.")

if __name__ == "__main__":
    app()