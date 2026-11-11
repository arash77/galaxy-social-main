"""TEST ENVIRONMENT ONLY: delete test posts of the accounts in plugins.yml since a given time.

Usage: python .github/scripts/test_cleanup.py HOURS [--delete]
Without --delete it only lists what it would remove (and who is logged in).
Mastodon and Bluesky may be personal accounts: only posts containing MARKER, and replies in
their threads, are removed. Matrix posts in a test room by a bot account: all its messages are removed.
"""
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from uuid import uuid4

import requests
import yaml

MARKER = "🧪 galaxy-social test"
hours, delete = float(sys.argv[1]), "--delete" in sys.argv
since = datetime.now(timezone.utc) - timedelta(hours=hours)
print(f"{'Deleting' if delete else 'Listing (dry run)'} posts since {since.isoformat()}\n")


def config_of(plugin):
    return {
        key: os.environ.get(value[1:], "") if isinstance(value, str) and value.startswith("$") else value
        for key, value in plugin["config"].items()
    }


def mastodon_cleanup(config):
    from mastodon import Mastodon

    client = Mastodon(access_token=config["access_token"], api_base_url=config["base_url"])
    me = client.account_verify_credentials()
    print(f"  logged in as @{me['acct']} on {config['base_url']} (locked: {me['locked']})")
    statuses, page = [], client.account_statuses(me["id"], limit=40)
    while page:
        statuses += [status for status in page if status["created_at"] >= since]
        if page[-1]["created_at"] < since:
            break
        page = client.fetch_next(page)
    test_ids = set()
    for status in reversed(statuses):  # oldest first, so a thread's root comes before its replies
        if MARKER in status["content"] or status["in_reply_to_id"] in test_ids:
            test_ids.add(status["id"])
            print(f"  {status['created_at']} {status['url']}")
            if delete:
                client.status_delete(status["id"])
        else:
            print(f"  keep (no marker) {status['created_at']} {status['url']}")


def bluesky_cleanup(config):
    from atproto import Client

    client = Client(config["base_url"])
    me = client.login(config["username"], config["password"])
    print(f"  logged in as @{me.handle}")
    posts, cursor = [], None
    while True:
        feed = client.get_author_feed(actor=me.did, cursor=cursor, limit=100)
        old = False
        for item in feed.feed:
            if item.reason or item.post.author.did != me.did:
                continue  # reposts and others' posts
            created = datetime.fromisoformat(item.post.record.created_at.replace("Z", "+00:00"))
            if created < since:
                old = True
                break
            posts.append((created, item.post))
        cursor = feed.cursor
        if old or not cursor:
            break
    test_uris = set()
    for created, post in sorted(posts, key=lambda p: p[0]):  # oldest first
        reply = post.record.reply
        if MARKER in post.record.text or (reply and reply.root.uri in test_uris):
            test_uris.add(post.uri)
            print(f"  {created} {post.uri}")
            if delete:
                client.delete_post(post.uri)
        else:
            print(f"  keep (no marker) {created} {post.uri}")


def matrix_cleanup(config):
    # plain client-server API: /messages without "from" reads back from the newest event (Matrix 1.3+)
    api = config["base_url"].rstrip("/") + "/_matrix/client/v3"
    headers = {"Authorization": f"Bearer {config['access_token']}"}
    response = requests.get(f"{api}/account/whoami", headers=headers)
    response.raise_for_status()
    user_id, room = response.json()["user_id"], quote(config["room_id"], safe="")
    print(f"  logged in as {user_id}, room {config['room_id']}")
    params = {"dir": "b", "limit": 100}
    while True:
        response = requests.get(f"{api}/rooms/{room}/messages", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        for event in data.get("chunk", []):
            if event["origin_server_ts"] / 1000 < since.timestamp():
                return
            content = event.get("content", {})
            if event["sender"] == user_id and event["type"] == "m.room.message" and content:
                print(f"  {datetime.fromtimestamp(event['origin_server_ts'] / 1000, timezone.utc)} {event['event_id']} {content.get('msgtype')} {content.get('info', {}).get('mimetype', '')}: {content.get('body', '')[:50]!r}")
                if delete:
                    requests.put(
                        f"{api}/rooms/{room}/redact/{quote(event['event_id'], safe='')}/{uuid4()}",
                        headers=headers,
                        json={"reason": "test cleanup"},
                    ).raise_for_status()
        if "end" not in data:
            return
        params["from"] = data["end"]


def linkedin_cleanup(config):
    author = f"urn:li:organization:{config['org_id']}"
    headers = {
        "Authorization": f"Bearer {config['access_token']}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202607",
    }
    print(f"  posting as {author}")
    response = requests.get(
        f"https://api.linkedin.com/rest/posts?author={quote(author)}&q=author&count=100&sortBy=CREATED",
        headers={**headers, "X-RestLi-Method": "FINDER"},
    )
    response.raise_for_status()
    for post in response.json().get("elements", []):
        created = datetime.fromtimestamp(post["createdAt"] / 1000, timezone.utc)
        if created < since:
            return
        print(f"  {created} https://www.linkedin.com/feed/update/{post['id']}")
        if delete:
            requests.delete(
                f"https://api.linkedin.com/rest/posts/{quote(post['id'])}",
                headers={**headers, "X-RestLi-Method": "DELETE"},
            ).raise_for_status()


cleanups = {
    "mastodon": mastodon_cleanup,
    "bluesky": bluesky_cleanup,
    "matrix": matrix_cleanup,
    "linkedin": linkedin_cleanup,
}
failed = False
with open("plugins.yml") as f:
    for plugin in yaml.safe_load(f)["plugins"]:
        kind = plugin["class"].split(".")[0]
        if not plugin["enabled"] or kind not in cleanups:
            continue
        print(f"{plugin['name']}:")
        try:
            cleanups[kind](config_of(plugin))
        except Exception as e:
            failed = True
            print(f"  ERROR: {type(e).__name__}: {e}")
sys.exit(1 if failed else 0)
