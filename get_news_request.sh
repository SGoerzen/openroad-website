curl -s \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  "https://discord.com/api/v10/channels/$DISCORD_CHANNEL_ID/messages?limit=10"