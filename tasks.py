from hapdb import parser, db
from invoke import task


@task
def new(ctx, path):
    with open(path) as f:
        lines = f.readlines()

    log_entries = parser.parse(lines)

    db_filepath = path + '.sqlite'
    print(db_filepath)
    db.init(db_filepath)
    db.ingest(log_entries)
