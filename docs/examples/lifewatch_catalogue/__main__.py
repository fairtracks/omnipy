"""Import the LifeWatch ERIC catalogue and print the start of each table."""

from .flows import import_lifewatch_catalogue

tables = import_lifewatch_catalogue.run()
for name, table in tables.items():
    print(f'{name}: {len(table.content)} rows')
    print(table.content.head())
    print()
