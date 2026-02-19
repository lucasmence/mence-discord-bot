# my-discord-bot
My personal discord bot for a friend private server.

# Install
Clone this repository:

```git clone https://github.com/lucasmence/my-discord-bot```

Insert the DISCORD_TOKEN in **docker-compose.yml** file:

``` 
environment:
      - DISCORD_TOKEN=<YOUR_DISCORD_TOKEN_HERE>
```

Let the docker set it up:

```sudo docker compose up -d --build```

Check if everything is okay:

```sudo docker logs discord-bot```

Enjoy!
