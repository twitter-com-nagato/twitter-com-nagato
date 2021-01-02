import json
import urllib.parse
import urllib.request


class YahooApi:
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
