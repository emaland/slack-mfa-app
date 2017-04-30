#!/usr/bin/env python

from bottle import redirect, request, route, run
from slackclient import SlackClient

import os
import requests
import shelve

client_id = os.environ.get("SLACK_CLIENT_ID")
client_secret = os.environ.get("SLACK_CLIENT_SECRET")

PORT = 8000

@route('/healthz')
def healthz():
    pass

@route('/mfabot/')
def defaultroute():
    auth_code = request.query.code
    sc = SlackClient("")

    auth_response = sc.api_call(
        "oauth.access",
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code
        )

    tokens = shelve.open("tokens")
    tokens[str(auth_response['team_id'])] = auth_response['access_token']
    tokens.close()

    sc = SlackClient(auth_response['access_token'])
    info = sc.api_call("team.info")

    redirect("https://" + info['team']['domain'] + ".slack.com/")

@route('/mfabot/mfanag', method='POST')
def mfanag():
      tokens = shelve.open("tokens")
      access_token = tokens[str(request.forms.get('team_id'))]
      response = "Thaanks mang"
      requests.post(request.forms.get('response_url'), '{"text":"' + response + '"}')
      sc = SlackClient(access_token)
      users = sc.api_call("users.list")['members']
      team_info = sc.api_call('team.info')
      domain = team_info.get('team').get('domain')
      faurl = "http://" + domain + ".slack.com/account/settings/2fa_choose"

      for user in users:
        if not user.get('is_bot') and not user.get('has_2fa') and user.get('name') == "emaland":
          print user.get('name')
          print sc.api_call("chat.postMessage", channel=user.get('id'), text='You currently do not have Multifactor Authentication configured.\n\nPlease enable Multifactor Authentication here: ' + faurl)

if __name__ == '__main__':
    run(host='0.0.0.0', port=PORT)


