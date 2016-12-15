# -*- coding: utf-8 -*-
# DISCLAIMER: The regular expressions used here are taken from
# https://github.com/gforcada/haproxy_log_analysis
from datetime import datetime

import re


# Example log line, to understand the regex below (truncated to fit into
# 80 chars):
#
# Dec  9 13:01:26 localhost haproxy[28029]: 127.0.0.1:39759
# [09/Dec/2013:12:59:46.633] loadbalancer default/instance8
# 0/51536/1/48082/99627 200 83285 - - ---- 87/87/87/1/0 0/67
# {77.24.148.74} "GET /path/to/image HTTP/1.1"

# From the above log line the first part
# `Dec  9 13:01:26 localhost haproxy[28029]:`
# is coming from syslog.
# The following regular expression takes care of finding it.
# With it, this syslog slug can be removed to make processing regular
# haproxy log lines possible.
SYSLOG_REGEX = re.compile(
    # Dec  9
    r'\A\w+\s+\d+\s+'
    # 13:01:26
    r'\d+:\d+:\d+\s+'
    # localhost haproxy[28029]:
    # note that can be either localhost or an IP or a hostname
    # and can also contain a dot in it
    r'(\w+|(\d+\.){3}\d+|[.a-zA-Z0-9_-]+)\s+\w+\[\d+\]:\s+',

)

HAPROXY_LINE_REGEX = re.compile(
    # 127.0.0.1:39759
    r'\A(?P<client_ip>(\d+\.){3}\d+):(?P<client_port>\d+)\s+'
    # [09/Dec/2013:12:59:46.633]
    r'\[(?P<accept_date>.*)\..*\]\s+'
    # loadbalancer default/instance8
    r'(?P<frontend_name>.*)\s+(?P<backend_name>.*)/(?P<server_name>.*)\s+'
    # 0/51536/1/48082/99627
    r'(?P<tq>-?\d+)/(?P<tw>-?\d+)/(?P<tc>-?\d+)/'
    r'(?P<tr>-?\d+)/(?P<tt>\+?\d+)\s+'
    # 200 83285
    r'(?P<status_code>-?\d+)\s+(?P<bytes_read>\+?\d+)\s+'
    # - - ----
    r'.*\s+'  # ignored by now, should capture cookies and termination state
    # 87/87/87/1/0
    r'(?P<act>\d+)/(?P<fe>\d+)/(?P<be>\d+)/'
    r'(?P<srv>\d+)/(?P<retries>\+?\d+)\s+'
    # 0/67
    r'(?P<queue_server>\d+)/(?P<queue_backend>\d+)\s+'
    # {77.24.148.74}
    r'((?P<request_headers>{.*})\s+(?P<response_headers>{.*})\s+|'
    r'(?P<headers>{.*})\s+|)'
    # "GET /path/to/image HTTP/1.1"
    r'"(?P<http_request>.*)"'
    r'\Z'  # end of line
)

HTTP_REQUEST_REGEX = re.compile(
    r'(?P<method>\w+)\s+'
    r'(?P<path>(/[`´\\<>/\w:,;\.#$!?=&@%_+\'\*^~|\(\)\[\]\{\}-]*)+)'
    r'\s+(?P<protocol>\w+/\d\.\d)'
)


def parse(lines):
    log_entries = []
    for line in lines:
        line = SYSLOG_REGEX.sub('', line)
        matches = HAPROXY_LINE_REGEX.match(line.strip())
        if matches is None:
            continue

        log_entry = dict(
            client_ip=matches.group('client_ip'),
            client_port=int(matches.group('client_port')),

            raw_accept_date=matches.group('accept_date'),
            accept_date=_parse_accept_date(matches.group('accept_date')),

            frontend_name=matches.group('frontend_name'),
            backend_name=matches.group('backend_name'),
            server_name=matches.group('server_name'),

            time_wait_request=int(matches.group('tq')),
            time_wait_queues=int(matches.group('tw')),
            time_connect_server=int(matches.group('tc')),
            time_wait_response=int(matches.group('tr')),
            total_time=matches.group('tt'),

            status_code=matches.group('status_code'),
            bytes_read=matches.group('bytes_read'),

            connections_active=matches.group('act'),
            connections_frontend=matches.group('fe'),
            connections_backend=matches.group('be'),
            connections_server=matches.group('srv'),
            retries=matches.group('retries'),

            queue_server=int(matches.group('queue_server')),
            queue_backend=int(matches.group('queue_backend')),

            captured_request_headers=matches.group('request_headers'),
            captured_response_headers=matches.group('response_headers'),

            raw_http_request=matches.group('http_request'),
        )

        if matches.group('headers') is not None:
            log_entry['captured_request_headers'] = matches.group('headers')

        log_entry.update(_parse_http_request(log_entry['raw_http_request']))

        log_entries.append(log_entry)

    return log_entries


def _parse_accept_date(raw_accept_date):
    return datetime.strptime(raw_accept_date, '%d/%b/%Y:%H:%M:%S')


def _parse_http_request(raw_http_request):
    result = {}
    matches = HTTP_REQUEST_REGEX.match(raw_http_request)
    if matches:
        return {
            'http_request_method': matches.group('method'),
            'http_request_path': matches.group('path'),
            'http_request_protocol': matches.group('protocol'),
        }
    else:
        return _handle_bad_http_request(raw_http_request)


def _handle_bad_http_request(raw_http_request):
    result = {
        'http_request_method': 'invalid',
        'http_request_path': 'invalid',
        'http_request_protocol': 'invalid',
    }

    if raw_http_request != '<BADREQ>':
        print('Could not process HTTP request {0}'.format(raw_http_request))

    return result
