import requests


def basic_get(url, params=None, headers=None, proxies=None):
    response = requests.get(url, params=params, headers=headers, proxies=proxies)
    return response
