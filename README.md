# masto-archiver
This script solves the pressing problem of accidentally making the same banger shitpost twice. If you run this, say, once a day, you can Ctrl+f through your previous posts to avoid that embarassing situation.

## Dependencies
You will need `Mastodon.py` and `jinja2`. Install them using pip: `pip install Mastodon.py jinja2`

## Usage
Fill in your data in `secret.py` (most importantly the instance address and a Mastodon access token that has the `read:accounts` and `read:statuses` scopes set), then run `archive.py`.

## Warning!
- The output of this thing includes private and unlisted toots by default so make sure to put the page in a place where only you can see it.
- This script is in no way optimized for speed. It can take a long time depending on the Mastodon server and the number of toots, especially if it runs into rate limits.

## To Do
- [x] include replies to yourself
- [ ] optionally include replies to others
- [ ] configurable private / unlisted / direct toots
- [x] indicate if post has a media attachment
- [x] show spoilers
- [x] show polls
- [x] Date Formatting
- [x] improve margins and such
- [x] Change to HTML Templating engine
- [x] Secrets File
- [x] Usage Instructions
- [ ] Screenshot for Github