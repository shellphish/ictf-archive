This contains the source for the blockchain game-server


To run:

```
docker run \
    --cap-add=NET_ADMIN \
    --rm \
    -p 8443:8443 \
    -p 4102:4102 \
    -v `realpath data`:/opt/buffalo/data \
    --name chall_buffalo_srv \
    chall_buffalo_srv
```

