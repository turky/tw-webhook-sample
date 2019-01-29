import hmac
import base64
import hashlib
import json
import logging
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
        tw_objects = request.json
        logger.log_text(json.dumps(tw_objects))
        client = datastore.Client()
        with client.transaction() as txs:
            cur_ent = datastore.entity.Entity()
            cur_ent.update(tw_objects)
            txs.put(cur_ent)
            return HTTPResponse(body='operation successed', status=200)
    except:
        raise
        #logger.log_text('Something Happend')
        #return HTTPError(status=500)

@app.error(404)
def error_404(error):
    return 'Sorry, Nothing at this URL'

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
