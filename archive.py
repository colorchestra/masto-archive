#!/usr/bin/python3
import datetime
from mastodon import Mastodon
from jinja2 import Environment, FileSystemLoader


output_file = 'index.html'
debug = False

exec(compile(source=open('secret.py').read(),filename='secret.py', mode='exec'))
masto = Mastodon(
    access_token = mastodon_access_token,
    api_base_url = mastodon_address,
    ratelimit_method='wait')
statuses_for_templating = []
timestamp_at_start = datetime.datetime.now()
jinja_env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True
)
template = jinja_env.get_template("masto-template.html")

def template_statuses(statuses):
    for one_status in statuses:
        if (
            visibility_options[one_status.visibility] == False or
            one_status.reblog
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
            ]:
            if one_status[attribute]:
                new_status[attribute] = one_status[attribute]

        # this needs an extrawurst because we don't want to copy the entire attachments dict
        if one_status['media_attachments']:
            new_status['media_attachments'] = True

        # this one does too because we want to format the time string
        if one_status['created_at']:
            new_status['created_at'] = one_status['created_at'].strftime('%Y-%m-%d %H:%M:%S')

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

        if debug:
            if len(statuses_for_templating) > 10:
                print(statuses_for_templating)
                break

    timestamp_before_rendering = datetime.datetime.now()
    creation_delta = timestamp_before_rendering - timestamp_at_start
    creation_duration = str(datetime.timedelta(seconds=creation_delta.seconds)) # clever trick(tm) to format the seconds correctly
    rendered_html = template.render(
        my_name=my_name,
        statuses_total=str(len(statuses_for_templating)),
        generated_time=timestamp_before_rendering.strftime('%Y-%m-%d %H:%M:%S'),
        statuses_out=statuses_for_templating,
        creation_duration=creation_duration,
        me=me
        )

    with open(output_file, 'w') as file:
        file.write(rendered_html)

me = masto.me()
uid = me['id']
me['created_at_formatted'] = str(me['created_at'].strftime('%Y-%m-%d'))

if __name__ == "__main__":
    run_thing()