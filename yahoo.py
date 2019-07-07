import json
import urllib.parse
import urllib.request


class Yahoo:
    def __init__(self, appid):
        self.appid = appid

    def api(self, apiurl, params, method='GET'):
        params['appid'] = self.appid
        params = urllib.parse.urlencode(params, encoding='UTF-8')
        if method == 'GET':
            response = urllib.request.urlopen("%s?%s" % (apiurl, params))
        elif method == 'POST':
            # Encode the query string to bytes
            params = params.encode('UTF-8')
            response = urllib.request.urlopen(apiurl, params)
        else:
            raise NotImplementedError('Method %s is not supported.' % method)

        response = response.read().decode('UTF-8')
        response = json.loads(response)

        # Handle errors
        if not isinstance(response, type({})):
            raise IOError('INVALID FORMAT "%s"' % response)
        if 'Error' in response:
            raise IOError('YAHOO! API ERROR "%s"' % response['Error'])

        return response

    def get_key_phrase(self, sentence):
        apiurl = 'http://jlp.yahooapis.jp/KeyphraseService/V1/extract'
        response = self.api(apiurl, {
            'output': 'json',
            'sentence': sentence,
        }, 'POST')
        if response:
            response = [k for k, v in sorted(
                response.items(), key=lambda x:x[1], reverse=True)]

        return response

    def search_item(self, queries, params):
        apiurl = 'http://shopping.yahooapis.jp/ShoppingWebService/V1/json/itemSearch'
        params['query'] = ' '.join(queries)
        response = self.api(apiurl, params)
        available = 0
        if response:
            response = response['ResultSet']
            available = int(response['totalResultsAvailable'])
            returned = int(response['totalResultsReturned'])
            response = [response['0']['Result'][str(i)] for i in range(returned)]

        return (response, available)
