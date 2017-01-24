#!/usr/bin/python3

VERSION=0.01

import argparse
import requests
import logging

import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.WARN)

# arguments parsing stuff
parser = argparse.ArgumentParser(
        description='Download Mediawiki Pages in raw and concat them!')
parser.add_argument('--url',      '-U',   dest='url',  metavar="<URL>", type=str, required=True)
parser.add_argument('--user',      '-u',   dest='user',  metavar="<username>", type=str)
parser.add_argument('--password',      '-p',   dest='pw',  metavar="<password>", type=str)
parser.add_argument('--namespace',      '-n',   dest='namespace',  metavar="<Namespace>", type=str)

args = parser.parse_args()

# Fires a request for bot
def request(url, params={}, reqtype='post', json=None, **kwargs):
    headers = {
      'User-Agent': 'MediaWiki OnePage {version}'.format(version=VERSION),
    }
    # TODO: remove verify False
    resp = requests.request(reqtype, url, data=params, headers=headers, json=json, verify=False, **kwargs)
    logging.warn("Return data: " + resp.text)
    return resp

def login(api, user, password):
    token = None

    # retrieve token
    resp = request(api, params={
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json',
    })

    try:
        data = resp.json()
        token = data['query']['tokens']['logintoken']
        logging.log(logging.DEBUG, 'Logintoken is: {token}'.format(token=token))

    except ValueError as e:
        raise SystemExit('Unable to process JSON data during login: {sg}'.format(msg=str(e)))
    except KeyError as e:
        raise SystemExit('Unable to retrieve token. No token received.')

    # Login with retrieved token and use password and username now
    resp = request(api, params={
        'action': 'login',
        'lgname': user,
        'lgpassword': password,
        'lgtoken': token,
        'format': 'json',
    })

    try:
        data = resp.json()
        if not data['login']['result'] == 'Success':
            raise SystemExit('Unable to login: result is {result}'.format(result = data['login']['result']))
    except ValueError as e:
        raise SystemExit('Unable to process JSON data during login: {msg}'.format(msg=str(e)))

    return token

def list_pages(api, token, namespaces=[]):

    sites = []

    if len(namespaces) > 0:
        resp = request(api, params={
            'action': 'query',
            'meta': 'siteinfo',
            'iprop': 'namespaces',
            'token': token,
            'format': 'json',
        })
        json = resp.json()

    def ns_id(space):
        for ns in json['query']['namespaces']:
            if ns['canonical'] == space:
                return ns['id']

        raise SystemExit('namespace "{ns}" not found in Wiki!'.format(ns=space))

    namespace_ids = map(ns_id, namespace)


    # get namespace ids
    # /w/api.php?action=query&format=json&meta=siteinfo&siprop=namespaces

    # {
    # "batchcomplete": "",
    # "query": {
    #     "namespaces": {
    #         "-2": {
    #             "id": -2,
    #             "case": "first-letter",
    #             "canonical": "Media",
    #             "*": "Media"
    #         },
    #         "-1": {
    #             "id": -1,
    #             "case": "first-letter",
    #             "canonical": "Special",
    #             "*": "Special"
    #         },




    for space in namespace_ids:
        resp = request(api, params={
            'action': 'query',
            'list': 'allpages',
            'apnamespace': space,
            'token': token,
            'format': 'json',
            })
        json = resp.json()

    #/w/api.php?action=query&format=json&list=allpages&apnamespace=11
    #
    # get pages from namespace ids
    #{
    #"batchcomplete": "",
    #"continue": {
    #    "apcontinue": "Abusefilter-brasilhot100",
    #    "continue": "-||"
    #},
    #"query": {
    #    "allpages": [
    #        {
    #            "pageid": 1314637,
    #            "ns": 8,
    #            "title": "MediaWiki:Aboutsite"
    #        },
    #        {
    #            "pageid": 23475160,
    #            "ns": 8,
    #            "title": "MediaWiki:Abusefilter"
    #        },
    return sites

def main():
    try:
        token = login(args.url, args.user, args.pw)
        pages = page_list(args.url, token, args.namespace)

        for page in pages:
            print_page(args.url, token, page)
    except KeyboardInterrupt as e:
        # Do nothing if interrupted via Ctrl+C
        raise SystemExit('Ending on KeyboardInterrupt.')
        pass

if __name__ == "__main__":
    main()
