# aimazing

I built this fantastic command line maze game, do you think you can solve it?

PS: You might want to run `stty -icanon` for the best gameplay experience.

## Resources

Research unsafe pickle deserialization in Python. There's a reason that many serialization libraries (e.g. pyyaml, pickle) mark some functions as unsafe.

- https://book.hacktricks.xyz/pentesting-web/deserialization
- https://checkoway.net/musings/pickle/

## Writeup

The challenge asks you to submit a gzip compressed sklearn classifier that will be (1) decompressed with zlib and (2) unpickled. it's technically possible to train a proper classifier and solve the maze, but the user input is directly passed to pickle.loads()

See [exploit.py](exploit.py)
