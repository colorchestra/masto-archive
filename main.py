#!/usr/bin/python3
import datetime
from mastodon import Mastodon

### Mastodon
mastodon_address = ''
mastodon_access_token = ''
masto = Mastodon(access_token = mastodon_access_token, api_base_url = mastodon_address)
statuses_out = []
output_file = 'index.html'

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

def write_html():
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


uid = masto.me()['id']
statuses = masto.account_statuses(uid, limit=40)
handle_statuses(statuses)
while hasattr(statuses, '_pagination_next'):
    print("Fetching more statuses. Currently we have " + str(len(statuses_out)))
    if masto.ratelimit_remaining < 50:
        print("Remaining until rate limit: " + str(masto.ratelimit_remaining))
    statuses = masto.fetch_next(statuses)
    handle_statuses(statuses)
    ### testing
    if len(statuses_out) > 10:
        break

write_html()