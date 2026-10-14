# Posts every member of a Discord server as a GuildPing import string to a Discord
# channel, inside a code block so it can be copied with one click:
#
#   GP2;U,Name,Name,123456789012345678;U,Other,Other,234567890123456789
#
# Each member is "U,<display name>,<display name>,<User ID>". Display names are
# normalized to plain letters (e.g. "Därk" -> "Dark", fancy Unicode -> normal text).
# Discord messages are limited to 2000 characters, so large lists are split into
# several posts. Each post is a complete GP2 string that can be imported on its own.
#
# Setup: fill in BOT_TOKEN and CHANNEL_LINK below (see README.md), then run
#        export_members.bat, or:  python export_members.py

import re
import sys
import time
import unicodedata

import discord

# ===================== SETTINGS =====================
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"        # Developer Portal > your app > Bot > Reset Token
CHANNEL_LINK = "PASTE_YOUR_CHANNEL_LINK_HERE"  # Discord: right-click the channel > Copy Link
# ====================================================

MAX_LEN = 2000  # Discord's message length limit


def normalize(name):
    """Turn a Discord display name into plain ASCII text that is safe in the GP2 format."""
    text = unicodedata.normalize("NFKC", name)          # fancy/styled letters -> normal letters
    text = unicodedata.normalize("NFKD", text)          # split accents off letters
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.encode("ascii", "ignore").decode()      # drop emoji and anything non-ASCII
    text = re.sub(r"[,;|`]", " ", text)                 # , ; separate fields, | breaks WoW chat, ` breaks code blocks
    return re.sub(r"\s+", " ", text).strip()


def build_posts(entries):
    """Split entries into messages that each fit Discord's limit and hold a complete GP2 string."""
    stamp = f"<t:{int(time.time())}:f>"
    head_room = len("**GuildPing import** - part 99 of 99 - 999 members - updated ") + len(stamp) + 20
    budget = MAX_LEN - head_room - len("GP2;")
    chunks, cur, size = [], [], 0
    for name, uid in entries:
        item = f"U,{name},{name},{uid}"
        if cur and size + len(item) + 1 > budget:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(item)
        size += len(item) + 1
    if cur:
        chunks.append(cur)
    posts = []
    for i, chunk in enumerate(chunks, 1):
        part = f" - part {i} of {len(chunks)}" if len(chunks) > 1 else ""
        posts.append(f"**GuildPing import**{part} - {len(chunk)} members - updated {stamp}\n"
                     f"```\nGP2;{';'.join(chunk)}\n```")
    return posts


m = re.search(r"/channels/(\d+)/(\d+)", CHANNEL_LINK)
if BOT_TOKEN.startswith("PASTE_") or not m:
    sys.exit("ERROR: open export_members.py and fill in BOT_TOKEN and CHANNEL_LINK first (see README.md).")
SERVER_ID, CHANNEL_ID = int(m.group(1)), int(m.group(2))

intents = discord.Intents.default()
intents.members = True  # needs "Server Members Intent" turned on in the Developer Portal
client = discord.Client(intents=intents)
result = {"ok": False}


@client.event
async def on_ready():
    try:
        guild = client.get_guild(SERVER_ID)
        if guild is None:
            print("ERROR: the bot can't see that server. Check CHANNEL_LINK and that the bot was invited.")
            return
        try:
            channel = await client.fetch_channel(CHANNEL_ID)
        except discord.NotFound:
            print("ERROR: channel not found. Check CHANNEL_LINK.")
            return
        except discord.Forbidden:
            print("ERROR: the bot can't see that channel. Give it View Channel there (see README.md).")
            return
        if not hasattr(channel, "send"):
            print("ERROR: the link points to a channel the bot can't post in (e.g. a forum or category). "
                  "Link a text channel or a forum post instead.")
            return

        members = [mb async for mb in guild.fetch_members(limit=None) if not mb.bot]

        entries, seen, skipped = [], {}, []
        # display_name = server nickname if set, otherwise their global Discord name
        for mb in members:
            name = normalize(mb.display_name) or normalize(mb.name)
            if not name:
                skipped.append(f"{mb.id}: display name has no usable letters")
                continue
            if name.lower() in seen:
                skipped.append(f"{mb.id}: '{name}' is the same name as user {seen[name.lower()]}")
                continue
            seen[name.lower()] = mb.id
            entries.append((name, mb.id))

        if not entries:
            print("ERROR: no members to post.")
            return
        entries.sort(key=lambda e: e[0].lower())

        posts = build_posts(entries)
        try:
            for post in posts:
                await channel.send(post, allowed_mentions=discord.AllowedMentions.none())
        except discord.Forbidden:
            print("ERROR: the bot isn't allowed to post in that channel. Give it Send Messages there (see README.md).")
            return

        print(f"Posted {len(entries)} members in {len(posts)} message(s) to {CHANNEL_LINK}")
        if skipped:
            print(f"\nSkipped {len(skipped)} member(s):")
            for s in skipped:
                print("  - " + s)
        result["ok"] = True
    finally:
        await client.close()


try:
    client.run(BOT_TOKEN, log_handler=None)
except discord.LoginFailure:
    sys.exit("ERROR: Discord rejected the bot token. Reset it in the Developer Portal and paste the new one.")
except discord.PrivilegedIntentsRequired:
    sys.exit("ERROR: turn on 'Server Members Intent' under Bot in the Developer Portal, then run again.")

sys.exit(0 if result["ok"] else 2)
