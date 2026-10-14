# Discord Member Export

Turns your Discord server's member list into a **GuildPing import string** and
posts it to a Discord channel as a code block, so anyone can copy it with one
click and paste it into GuildPing's **Import Mappings**.

```
GP2;U,Example Name,Example Name,123456789012345678;U,Another,Another,234567890123456789
```

- Starts with `GP2;`, then one entry per member, separated by `;`
- Each entry is `U,<display name>,<display name>,<User ID>` (`U` = user)
- Display name = their server nickname, or their Discord name if none is set
- Bots are left out; sorted A to Z by display name
- Discord messages are limited to 2,000 characters, so a big server is split into
  several posts ("part 1 of 2", ...). **Each post is a complete import string**
  and can be imported on its own.

## What's in the package

| File | What it does |
|---|---|
| `export_members.bat` | **The one you run.** Installs Python and discord.py if missing, then runs the export. |
| `export_members.py` | Uses your Discord bot to read the member list and post the import string. |
| `README.md` | This file. |

## Requirements

- Windows 10 or 11
- Permission to manage the Discord server (to add a bot)
- Python 3 (the `.bat` installs it automatically through winget if it's missing)

---

## Step 1: Create the Discord bot (one time)

1. Go to <https://discord.com/developers/applications> and sign in.
2. Click **New Application**, name it (e.g. `Member Export`), and click **Create**.
3. Open the **Bot** tab on the left.
4. Click **Reset Token**, confirm, and **copy the token**. You only see it once.
   Treat it like a password: anyone with it can control the bot.
5. On the same page, under **Privileged Gateway Intents**, turn on
   **Server Members Intent** and click **Save Changes**.
   Without this the bot can't see the member list.
6. Optional: turn off **Public Bot** so only you can add it to servers.

## Step 2: Invite the bot to your server (one time)

1. Open the **OAuth2** tab, then **URL Generator**.
2. Under **Scopes**, tick **bot**.
3. Under **Bot Permissions**, tick:
   - **View Channels**
   - **Send Messages**
   - **Send Messages in Threads** (only needed if you post to a forum post or thread)
4. Copy the **Generated URL** at the bottom, open it in your browser, pick your
   server, and click **Authorize**.

If the channel you post to is private, also add the bot (or its role) to that
channel: **Edit Channel → Permissions → Add members or roles**, and allow
**View Channel** and **Send Messages**.

The bot shows up offline in your member list. That's normal: it only comes online
for a few seconds while the export runs.

## Step 3: Copy the channel link

Right-click the channel (or forum post) where the import string should be
posted and click **Copy Link**. It looks like:

```
https://discord.com/channels/<server id>/<channel id>
```

## Step 4: Set up the script (one time)

1. Unzip this package to a folder, e.g. `C:\Tools\DiscordMemberExport`.
2. Open `export_members.py` in Notepad and fill in the settings:
   ```python
   BOT_TOKEN = "your-bot-token-here"
   CHANNEL_LINK = "https://discord.com/channels/123456789012345678/234567890123456789"
   ```
   Both go in quotes. To post somewhere else later, just change `CHANNEL_LINK`.

## Step 5: Run it

Double-click `export_members.bat`. When it finishes, the import string is posted
in your channel. Each run makes a new post; delete old ones if you don't need them.

The first run may take a minute or two while Python and discord.py install.

---

## Importing into GuildPing

1. In Discord, hover over the code block and click the **copy** icon in its corner
   (or select the text inside it and press **Ctrl+C**).
2. In game, type `/gp manage` and click **Import Mappings**.
3. Paste with **Ctrl+V**, click **Review Changes**, check the summary, then
   **Apply Changes**.
4. If the list was split into several parts, repeat for each part.

## How display names are cleaned up

So names can be typed in game, each display name is converted to plain letters:

| In Discord | In the export |
|---|---|
| Accented letters, e.g. `Därk` | `Dark` |
| Styled Unicode letters, e.g. fancy or full-width text | Normal letters |
| Emoji and other symbols outside plain text | Removed |
| `,` `;` `\|` `` ` `` (these break the import format, WoW chat, or the code block) | Replaced with a space |

Spaces and ordinary punctuation such as `.` `/` `-` `(` `)` are kept.

Some members are **skipped** and listed in the window at the end of the run:

- **No usable letters:** the name is only emoji or symbols, and so is their
  Discord name. Ask them to set a server nickname, or add them by hand.
- **Same name as another user:** two names become identical after clean-up.
  Only the first is kept; ask one to change their nickname.

## Troubleshooting

| Message | Fix |
|---|---|
| `fill in BOT_TOKEN and CHANNEL_LINK first` | Do Step 4.2. The link must contain `/channels/<number>/<number>`. |
| `Discord rejected the bot token` | The token is wrong or was reset. Reset it again (Step 1.4) and paste the new one. |
| `turn on 'Server Members Intent'` | Do Step 1.5. |
| `the bot can't see that server` | The bot isn't in the server (Step 2), or the link is from a different server. |
| `channel not found` | Copy the channel link again (Step 3). |
| `the bot can't see that channel` | Give the bot **View Channel** in that channel (Step 2). |
| `the bot isn't allowed to post in that channel` | Give the bot **Send Messages** (and **Send Messages in Threads** for forum posts) in that channel. |
| `a channel the bot can't post in` | The link points to a forum or category. Link a text channel or a specific forum post. |
| `Python was installed but could not be found` | Close the window and run the `.bat` again. Windows needs a new window to see the fresh install. |
| `winget is not available` | Install Python from <https://www.python.org/downloads/> and tick **Add python.exe to PATH**. |

## Security notes

- Never share `export_members.py` once your token is in it. If the token leaks,
  click **Reset Token** in the Developer Portal right away; the old one stops working.
- The posted import string contains every member's display name and Discord User ID.
  Post it in a channel only your members (or officers) can see.
- The bot only reads the member list and posts in the channel you choose. Its posts
  can't ping anyone: mentions are turned off.
- Don't use browser scripts or extensions that ask for your *personal* Discord
  token. That counts as a "self-bot", which breaks Discord's rules and can get
  your account banned. A real bot (this package) is the supported way.
