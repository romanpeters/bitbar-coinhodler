#!/usr/bin/env python
# coding=utf-8

# -*- coding: utf-8 -*-
# <bitbar.title>Coinhodler Portfolio</bitbar.title>
# <bitbar.version>v1.0.0</bitbar.version>
# <bitbar.author>Roman Peters</bitbar.author>
# <bitbar.author.github>romanpeters</bitbar.author.github>
# <bitbar.desc>Show current portfolio from coinhodler.io</bitbar.desc>
# <bitbar.image>hhttps://github.com/romanpeters/bitbar_coinhodler/blob/master/sample.png</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/romanpeters/bitbar_coinhodler</bitbar.abouturl>

# See https://github.com/romanpeters/bitbar_coinhodler for more info

import sys
import requests
import json
from builtins import input


token = ""  # saved from user input
currency = ""  # saved from user input


def get_info():
    global token, currency
    print("Run in terminal...")

    # get token
    while not token:
        passphrase = input('Paste your coinhodler.io passphrase here: ')
        url = 'https://api.coinhodler.io/v1/restore'
        req = requests.post(url, data={'passphrase': passphrase})
        json_value = json.loads(req.text)
        if json_value['status'] != 'success':
            print(json_value)
            token = None
        else:
            token = json_value['data']['token']

    # get currency
    while not currency:
        currency = input('Enter your prefered fiat currency code (EUR, USD, etc.): ').upper()
        url = "https://cdn.api.coinranking.com/v1/public/coins?base={}".format(currency)
        req = requests.get(url)
        json_value = json.loads(req.text)
        if json_value['status'] != 'success':
            print(json_value)
            currency = None

    # get symbol
    symbol = input('Enter your prefered fiat currency symbol (€, $, etc.) or leave empty for no symbol: ')
    if symbol:
        currency = "{}/{}".format(currency, symbol)

    # read
    with open(sys.argv[0], 'r') as f:
        app = f.readlines()

    # adjust
    new_app = []
    for line in app:
        if '=' in line:
            if line.startswith('token'):
                line = 'token = "{}"  # saved from user input\n'.format(token)
            elif line.startswith('currency'):
                line = 'currency = "{}"  # saved from user input\n'.format(currency)
        new_app.append(line)

    # write
    with open(sys.argv[0], 'w') as f:
        f.writelines(new_app)


def get_holdings(token):
    url = 'https://api.coinhodler.io/v1/hodler/rows'
    req = requests.get(url, headers={'X-Access-Token': token})
    holdings = json.loads(req.text)['data']['rows']
    return holdings


def get_values(holdings, base):
    ids = [str(h['coinrankingId']) for h in holdings]
    url = "https://cdn.api.coinranking.com/v1/public/coins?base={}&ids={}".format(base, '%2C'.join(ids))
    req = requests.get(url)
    values = json.loads(req.text)
    return values


def filter_output(token, base):
    holdings = get_holdings(token)
    values = get_values(holdings, base)
    result = []
    total_value = 0

    for hodl in holdings:
        result_item = {}
        id = hodl['coinrankingId']
        result_item['amount'] = hodl['amount']

        for item in values['data']['coins']:
            if item['id'] == id:
                break
        result_item['name'] = item['name']
        result_item['symbol'] = item['symbol']
        result_item['price'] = float(item['price'])
        result_item['change'] = item['change']
        result_item['icon'] = item['iconUrl']
        result_item['value'] = float(item['price']) * float(hodl['amount'])
        total_value += result_item['value']
        result.append(result_item)
    return sorted(result, key=lambda k: k['value'])[::-1], total_value


def main():
    if not token or not currency:
        get_info()

    if '/' in currency:
        base, symbol = currency.split('/')
    else:
        base, symbol = currency, ''

    holdings, total_value = filter_output(token, base)
    refresh_interval = sys.argv[0].split('.')[1]

    # format value
    if total_value > 10000:
        ft_value = total_value/1000
        print("{:.1f}| size=12".format(ft_value))
    elif total_value > 1000:
        ft_value = int(total_value)
        print("{}| size=12".format(ft_value))
    else:
        ft_value = total_value
        print("{:.2f}| size=12".format(ft_value))

    print("---")
    print("Portfolio: {}{:,.2f} | href=https://coinhodler.io".format(symbol, total_value))
    print("---")
    print('Asset\tPrice\t\tAmount\t\tValuation\t24h Change')
    for h in holdings:
        print('{:<6s}\t{}{:<12,.2f}\t{:<13.2f}\t{}{:<12,.2f}\t{:.2f}% | color={:s} href={:s}'.format(
                                            h['symbol'],
                                            symbol,
                                            h['price'],
                                            h['amount'],
                                            symbol,
                                            h['value'],
                                            h['change'],
                                            'darkred' if h['change'] < 0 else 'darkgreen',
                                            "https://coinmarketcap.com/currencies/{}/".format(h['name'])
                                            ))


if __name__ == '__main__':
    main()
