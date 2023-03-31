#!/usr/bin/python3
import datetime
from mastodon import Mastodon
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape

### Mastodon
exec(compile(source=open('secret.py').read(),filename='secret.py', mode='exec'))
masto = Mastodon(access_token = mastodon_access_token, api_base_url = mastodon_address)
statuses_out = []
statuses_out_for_templating = []
output_file = 'index.html'
timestamp_at_start = datetime.datetime.now()


env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=False
)
template = env.get_template("mytemplate.html")

def handle_statuses_for_templating(statuses):
    for one in statuses:
        if (
            one.reblog or
#            (hasattr(one, 'in_reply_to_account_id') and one.in_reply_to_account_id != uid) or
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
        '''
        if one.spoiler_text:
            new_status['spoiler_text'] = one.spoiler_text
        if one.content:
            new_status['content'] = one.content
        if one.media_attachments:
            new_status['media_attachments'] = one.media_attachments
        if one.poll:
            new_status['poll'] = one.poll
            '''

        statuses_out_for_templating.append(new_status)

def handle_statuses(statuses):
    for one_status in statuses:
        if (
            one_status.reblog or
            one_status.in_reply_to_account_id != uid or
            one_status.visibility == "direct"
            ):
            continue
        else:
            new_status = f'<div class="toot">'
            if one_status.spoiler_text:
                new_status += f"<em>{one_status.spoiler_text}</em><br />"
            if one_status.content == "":
                new_status += "<p><em>Toot has no text content</em></p>"
            else:
                new_status += f"{one_status.content}"
            if one_status.media_attachments:
                new_status += "🖼️<br />"
            if one_status.poll:
                poll_string = "<b>Poll:</b><br />"
                for option in one_status.poll.options:
                    poll_string += f"{option.title}: {option.votes_count}<br />"
                new_status += poll_string
            new_status += f"<small>⮌ {one_status.replies_count} ★ {one_status.favourites_count} ⭯ {one_status.reblogs_count}</small><br />"
            new_status += f"<small><a href='{one_status.url}'> {one_status.created_at:%Y-%m-%d_%H:%M:%S%z}</a></small>"
            new_status += "</div>"

            statuses_out.append(new_status)

def write_html(scheissdreck):
    with open('partial_header.html', 'r') as headerfile:
        headerstring = headerfile.read()

    with open('partial_footer.html', 'r') as footerfile:
        footerstring = footerfile.read()

    with open(output_file, 'w') as file:
        file.write(headerstring)
        file.write(f"<b>Toots here: {len(statuses_out)}; generated: {datetime.datetime.now():%Y-%m-%d_%H:%M:%S%z}</b></br>")
        for k in statuses_out:
            file.write(k + '\n')
        file.write(footerstring)

    with open('kackpisse.html', 'w') as file:
        file.write(scheissdreck)

def run_thing():
    statuses = masto.account_statuses(uid, limit=40) # 40 is the default server-side limit
    handle_statuses_for_templating(statuses)
    while hasattr(statuses, '_pagination_next'):
        print("Fetching more statuses. Currently we have " + str(len(statuses_out_for_templating)))
        if masto.ratelimit_remaining < 50:
            print("Remaining until rate limit: " + str(masto.ratelimit_remaining))
        statuses = masto.fetch_next(statuses)
        handle_statuses_for_templating(statuses)
        ### testing
        if len(statuses_out_for_templating) > 10:
            print(statuses_out_for_templating)
            break

    timestamp_before_rendering = datetime.datetime.now()
    scheissdreck = template.render(
        dummer_name="stinkmann",
        statuses_total=str(len(statuses_out_for_templating)),
        generated_time=timestamp_before_rendering, # TODO formatting
        toots=statuses_out_for_templating,
        statuses_out=statuses_out_for_templating,
        creation_duration=timestamp_before_rendering - timestamp_at_start,
        me=me
        )
    write_html(scheissdreck)

me = masto.me()
print(me)
uid = me['id']
#uid = masto.me()['id']

if __name__ == "__main__":
    run_thing()