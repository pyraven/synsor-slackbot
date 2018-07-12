import re
import os
from slackclient import SlackClient
import time
from datetime import datetime

# Authentication
slack_client = SlackClient(os.environ.get('YOUR_TOKEN_HERE'))

# Valid IP Only Regex
IP_REGEX = "^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]" \
          "[0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"

# Current Time
now = datetime.now().strftime('%m-%d-%Y %H:%M:%S')


def return_user(userid):
    user_list = slack_client.api_call("users.list")
    for info in user_list["members"]:
        if info["id"] == userid:
            return info["name"]


def parse_message(slack_message, slack_channel, slack_user):
    matches = re.search(IP_REGEX, slack_message)
    if matches:
        ipv4 = matches.group(0)
        ip = ipv4.split('.')
        third_octet, fourth_octet = ip[2], ip[3]
        identified_user = return_user(slack_user)
        warning = ("IP: XXX.XXX.{}.{} - Identified. @{} Please do not share IP Addresses on Slack. "
                   "Thank you.".format(third_octet, fourth_octet, identified_user))
        slack_client.api_call("chat.postMessage", link_names=1, channel=slack_channel, text=warning)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("{} - IP Synsor Bot Online. Searching...".format(now))
        while True:
            slack_events = (slack_client.rtm_read())
            for event in slack_events:
                    if event["type"] == "message" and not "subtype" in event:
                        user, channel = event["user"], event["channel"]
                        parse_message(event["text"], channel, user)
            time.sleep(1)
    else:
        print("Connection Issue.")