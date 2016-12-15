import os
from pony import orm
from datetime import datetime


db = orm.Database()


class LogEntry(db.Entity):
    client_ip = orm.Required(str)
    client_port = orm.Required(int)
    raw_accept_date = orm.Required(str)
    accept_date = orm.Required(datetime, 6)
    frontend_name = orm.Required(str)
    backend_name = orm.Required(str)
    server_name = orm.Required(str)
    time_wait_request = orm.Required(int)
    time_wait_queues = orm.Required(int)
    time_connect_server = orm.Required(int)
    time_wait_response = orm.Required(int)
    total_time = orm.Required(str)
    status_code = orm.Required(int)
    bytes_read = orm.Required(int)
    connections_active = orm.Required(int)
    connections_frontend = orm.Required(int)
    connections_backend = orm.Required(int)
    connections_server = orm.Required(int)
    retries = orm.Required(int)
    queue_server = orm.Required(int)
    queue_backend = orm.Required(int)
    captured_request_headers = orm.Optional(str, nullable=True)
    captured_response_headers = orm.Optional(str, nullable=True)
    raw_http_request = orm.Required(str)
    http_request_method = orm.Required(str)
    http_request_path = orm.Required(str)
    http_request_protocol = orm.Required(str)


@orm.db_session
def ingest(log_entries):
    [LogEntry(**log_entry) for log_entry in log_entries]
    db.commit()


def init(path):
    db.bind('sqlite', os.path.abspath(path), create_db=True)
    db.generate_mapping(create_tables=True)
