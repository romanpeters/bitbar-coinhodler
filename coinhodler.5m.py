#!/Users/romanpeters/Projects/Python/bitbar/venv/bin/python
# -*- coding: utf-8 -*-
# <bitbar.title>Coinhodler Portfolio</bitbar.title>
# <bitbar.version>v1.0.0</bitbar.version>
# <bitbar.author>Roman Peters</bitbar.author>
# <bitbar.author.github>romanpeters</bitbar.author.github>
# <bitbar.desc>Show current portfolio from coinhodler.io</bitbar.desc>
# <bitbar.image>https://coinhodler.io/static/media/logo.a996433a.svg</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
import sys
import requests
import json

token = ""
currency = ""


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
        url = f"https://cdn.api.coinranking.com/v1/public/coins?base={currency}"
        req = requests.get(url)
        json_value = json.loads(req.text)
        if json_value['status'] != 'success':
            print(json_value)
            currency = None

    # read
    with open(sys.argv[0], 'r') as f:
        app = f.readlines()

    # adjust
    new_app = []
    for line in app:
        if '=' in line:
            if line.startswith('token'):
                line = f'token = "{token}"  # saved from user input\n'
            elif line.startswith('currency'):
                line = f'currency = "{currency}"  # saved from user input\n'
        new_app.append(line)

    # write
    with open(sys.argv[0], 'w') as f:
        f.writelines(new_app)


# def get_token() -> str:
#     passphrase = None
#     while not passphrase:
#         print("Run in terminal...")
#         passphrase = input('Paste your coinhodler.io passphrase here: ')
#         url = 'https://api.coinhodler.io/v1/restore'
#         req = requests.post(url, data={'passphrase': passphrase})
#         json_value = json.loads(req.text)
#         if json_value['status'] != 'success':
#             print(json_value)
#             passphrase = None
#     return json_value['data']['token']
#
#
# def get_currency() -> str:
#     currency = None
#     while not currency:
#         currency = input('Enter your prefered fiat currency code (EUR, USD, etc.): ').upper()
#         url = f"https://cdn.api.coinranking.com/v1/public/coins?base={currency}"
#         req = requests.get(url)
#         json_value = json.loads(req.text)
#         if json_value['status'] != 'success':
#             print(json_value)
#             currency = None
#     return currency


def get_holdings(token):
    url = 'https://api.coinhodler.io/v1/hodler/rows'
    req = requests.get(url, headers={'X-Access-Token': token})
    holdings = json.loads(req.text)['data']['rows']
    return holdings


def get_values(holdings, base='EUR'):
    ids = [str(h['coinrankingId']) for h in holdings]
    url = f"https://cdn.api.coinranking.com/v1/public/coins?base={base}&ids={'%2C'.join(ids)}"
    req = requests.get(url)
    values = json.loads(req.text)
    return values


def filter_output(token):
    holdings = get_holdings(token)
    values = get_values(holdings)
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
    return sorted(result, key=lambda k: k['value'])[::-1] , total_value


def main():
    # try:
    #     with open('coinhodler_data.txt', 'r') as f:
    #         token, currency = f.readlines()
    #         token, currency = token.strip(), currency.strip()
    #     print(f'Token loaded!\nLanguage: {currency}\n')
    # except (FileNotFoundError, ValueError) as e:
    #     print(e)
    #     token = get_token()
    #     currency = get_currency()
    #     with open('coinhodler_data.txt', 'w+') as f:
    #         f.write(f"{token}\n{currency}")
    #     print(f'Token saved!\nFiat value: {currency}\n')

    get_info()

    holdings, total_value = filter_output(token)
    refresh_interval = sys.argv[0].split('.')[1]
    ft_value = total_value
    if ft_value > 1000:
        ft_value = total_value/1000
    print("{:.1f}| size=12".format(ft_value))
    print("---")
    print("Portfolio: {:,.2f} | href=https://coinhodler.io".format(total_value))
    print("---")
    print('Asset\tPrice\t\tAmount\t\tValuation\t24h Change')
    for h in holdings:
        print('{:<6s}\t{:<12,.2f} \t{:<13.2f}\t{:<12,.2f}\t{:.2f}% | color={:s} href={:s}'.format(
                                            h['symbol'],
                                            h['price'],
                                            h['amount'],
                                            h['value'],
                                            h['change'],
                                            'darkred' if h['change'] < 0 else 'darkgreen',
                                            f"https://coinmarketcap.com/currencies/{h['name']}/"
                                            ))


if __name__ == '__main__':
    main()
