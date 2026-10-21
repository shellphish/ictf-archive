# Description

- Name: `espresso`
- Difficulty / Category: hard / undergrad

# Deploy

```bash
docker build -t espresso -f ./Dockerfile .
docker run -itd --name espresso_test espresso
```

This runs the challenge inside a container `espresso_test` at port 11239. 

Users can visit the challenge through nc:

```bash
nc <IP of the container> 11239
```

# Deliveries to Players

All the files under the [to_players](./to_players/) directory should be delivered to the players.

```bash
zip ./espresso.zip -r ./to_players
# Now, deliver espresso.zip to the players.
```

# Solution

Please refer to the [writeup](./writeup/) directory.