"""TEST ENVIRONMENT ONLY: delete what the test accounts in plugins.yml posted since a given time.

Usage: python .github/scripts/test_cleanup.py HOURS [--delete]
Without --delete it only lists what it would remove (and who is logged in).
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import requests
import yaml

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
    page = client.account_statuses(me["id"], limit=40)
    while page:
        for status in page:
            if status["created_at"] < since:
                return
            print(f"  {status['created_at']} {status['url']}")
            if delete:
                client.status_delete(status["id"])
        page = client.fetch_next(page)


def bluesky_cleanup(config):
    from atproto import Client

    client = Client(config["base_url"])
    me = client.login(config["username"], config["password"])
    print(f"  logged in as @{me.handle}")
    cursor = None
    while True:
        feed = client.get_author_feed(actor=me.did, cursor=cursor, limit=100)
        for item in feed.feed:
            if item.reason or item.post.author.did != me.did:
                continue  # reposts and others' posts
            created = datetime.fromisoformat(item.post.record.created_at.replace("Z", "+00:00"))
            if created < since:
                return
            print(f"  {created} {item.post.uri}")
            if delete:
                client.delete_post(item.post.uri)
        cursor = feed.cursor
        if not cursor:
            return


async def matrix_cleanup_async(config):
    from nio import AsyncClient

    client = AsyncClient(config["base_url"])
    client.access_token = config["access_token"]
    try:
        user_id = (await client.whoami()).user_id
        client.user_id = user_id
        room_id = config["room_id"]
        print(f"  logged in as {user_id}, room {room_id}")
        sync = await client.sync(timeout=0, sync_filter={"room": {"rooms": [room_id], "timeline": {"limit": 50}}})
        timeline = sync.rooms.join[room_id].timeline
        events, token = list(reversed(timeline.events)), timeline.prev_batch
        while True:
            for event in events:
                if not hasattr(event, "server_timestamp"):
                    continue  # events nio could not parse
                if event.server_timestamp / 1000 < since.timestamp():
                    return
                content = event.source.get("content", {})
                if event.sender == user_id and event.source.get("type") == "m.room.message" and content:
                    print(f"  {datetime.fromtimestamp(event.server_timestamp / 1000, timezone.utc)} {event.event_id} {content.get('msgtype')}: {content.get('body', '')[:50]!r}")
                    if delete:
                        await client.room_redact(room_id, event.event_id, "test cleanup")
            if not token:
                return
            response = await client.room_messages(room_id, start=token, limit=100)
            if not response.chunk:
                return
            events, token = response.chunk, response.end
    finally:
        await client.close()


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
    "matrix": lambda config: asyncio.run(matrix_cleanup_async(config)),
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
