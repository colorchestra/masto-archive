#!/usr/bin/python3
import datetime
from mastodon import Mastodon
from jinja2 import Environment, FileSystemLoader

### Mastodon
exec(compile(source=open('secret.py').read(),filename='secret.py', mode='exec'))
masto = Mastodon(access_token = mastodon_access_token, api_base_url = mastodon_address)
statuses_for_templating = []
output_file = 'index.html'
timestamp_at_start = datetime.datetime.now()


env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=False
)
template = env.get_template("masto-template.html")

def template_statuses(statuses):
    for one in statuses:
        if (
            one.reblog or
            one.visibility == "direct"
            ):
            continue

        new_status = {}
        for attribute in [
            'spoiler_text',
            'poll',
            'content',
            'replies_count',
            'favourites_count',
            'reblogs_count',
            'url',
            'created_at'
            ]:
            if one[attribute]:
                new_status[attribute] = one[attribute]

        # this needs an extrawurst because we don't want to copy the entire attachments dict
        if one['media_attachments']:
            new_status['media_attachments'] = True

        statuses_for_templating.append(new_status)

def run_thing():
    statuses = masto.account_statuses(uid, limit=40) # 40 is the default server-side limit
    template_statuses(statuses)
    while hasattr(statuses, '_pagination_next'):
        print("Fetching more statuses. Currently we have " + str(len(statuses_for_templating)))
        if masto.ratelimit_remaining < 50:
            print("Remaining until rate limit: " + str(masto.ratelimit_remaining))
        statuses = masto.fetch_next(statuses)
        template_statuses(statuses)
        ### testing
        if len(statuses_for_templating) > 10:
            print(statuses_for_templating)
            break

    timestamp_before_rendering = datetime.datetime.now()
    rendered_html = template.render(
        my_name=my_name,
        statuses_total=str(len(statuses_for_templating)),
        generated_time=timestamp_before_rendering, # TODO formatting
        statuses_out=statuses_for_templating,
        creation_duration=timestamp_before_rendering - timestamp_at_start,
        me=me
        )

    with open(output_file, 'w') as file:
        file.write(rendered_html)

me = masto.me()
uid = me['id']

if __name__ == "__main__":
    run_thing()