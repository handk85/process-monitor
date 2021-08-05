from enum import Enum
import requests
HEADER = {"Content-Type": "application/json"}


class WebhookMessage:
    JSON_TEMPLATE = ""

    def __init__(self, url: str, title: str, message: str, additional_data: dict):
        self.url = url
        self.title = title
        self.message = message
        self.additional_data = additional_data

    def get_message(self):
        pass


class WebhookTypes(Enum):
    MS_TEAMS = "MSTeams"

    # TODO: need to add support
    SLACK = "Slack"


class MSTeamsMessage(WebhookMessage):
    JSON_TEMPLATE = '''{
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "5bc0de",
        "summary": "%s",
        "sections": [{
            "activityTitle": "%s",
            "activitySubtitle": "%s",
            "activityImage": "https://teamsnodesample.azurewebsites.net/static/img/image5.png",
            "facts": %s,
            "markdown": true
        }]
    }
    '''

    def __init__(self, url: str, title: str, message: str, additional_data: dict = {}):
        super().__init__(url, title, message, additional_data)

    def get_message(self):
        formatted_facts = [{'name': k, 'value': v} for k, v in self.additional_data.items()]
        return self.JSON_TEMPLATE % (self.title, self.title, self.message, str(formatted_facts))


webhook_type_map = {WebhookTypes.MS_TEAMS: MSTeamsMessage}


def send_webhook(message: WebhookMessage):
    requests.post(message.url, data=message.get_message(), headers=HEADER)


def get_webhook_type(webhook_url: str):
    if "office.com" in webhook_url:
        return WebhookTypes.MS_TEAMS
    if "slack.com" in webhook_url:
        return WebhookTypes.SLACK

    raise Exception("Cannot guess the type of webhook service from the webhook URL %s", webhook_url)
