import hmac
import base64
import hashlib
import json
from bottle import Bottle, request, HTTPResponse, HTTPError
from google.cloud import datastore, logging
from settings import TWITTER_CONSUMER_SECRET

app = Bottle()

@app.route('/')
def hello():
    return "Hello Bottle!"

@app.route('/webhook', method='GET')
def crc_digest():
    sha256_hash_digest = hmac.new(TWITTER_CONSUMER_SECRET.encode(),
                                  msg=request.query['crc_token'].encode(), digestmod=hashlib.sha256).digest()
    response = {
        'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest).decode()
    }
    return json.dumps(response)

@app.route('/webhook', method="POST")
def treat_webhook():
    log_client  = logging.Client()
    logger = log_client.logger('dev_log')
    try:
        for cur_item in request.json:
            cur_item = request.json
            cur_id = cur_item['id_str']
            logger.log_text(cur_id)
            client = datastore.Client()
            with client.transaction() as txs:
                cur_ent = datastore.entity.Entity(client.key("tw_object", cur_id))
                cur_ent.update(cur_item)
                txs.put(cur_ent)
        return HTTPResponse(body='operation successed', status=200)
    except:
        logger.log_text('Something Happend with {}'.format(str(request.json)))
        return HTTPError(status=500)

@app.error(404)
def error_404(error):
    return 'Sorry, Nothing at this URL'

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
