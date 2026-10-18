# Swiss Keys

_Secure like the Pope._


## The Service

It's an online password vault for Ethereum keys.  You can create a new key by
POSTing to `/new` with a password and (optionally) a comment; the server creates
a key and sends you back its address and a version number.

You can get the public and secret keys by POSTing to `/get` with an address and
the corresponding password.  You can also update keys by POSTing to `/set`, but
the only thing you can change is the comment.

The idea is pretty simple, but the implementation is not.  On the server, each
POST request creates a long-running "secure worker" process that does most of
the work.  This is actually an Ash shell, 'cause to be properly Swiss the server
needs to run in an Alpine container. The binary then calls itself with different
commands by writing to the shell's standard input, and collects the output by
reading from the shell's output streams.

It was a huge pain to get working.  The `shellout()` function contains egregious
`time.sleep(...)`s, and it's still kinda flaky.  See `source/shell.go` for the
gruesome details.


## Path Traversal

The first thing you notice when connecting to the server is that the certificate
is out of date and has a dangerously small RSA key, but that's a red herring -
it's just aesthetic.

The first real weakness is a sorta-path-traversal attack on the static file
server.  It serves files relative to the current directory, and keys are stored
in the `append` subdirectory.  So if you know the filename for the key you want
to steal, you can request it from the server directly!

This'll take a little work, though.  The key files have a "secure prefix" to
make them allegedly unguessable...  This is calculated as a keyed Blake2B HMAC
of the address - but the "secret" key is hardcoded in the binary, and the same
for everyone (see `SecretPrefix()` in `source/crypto.go`).

Then there are these random capital letters in the address part of the filename;
the address you know is all lower case.  But real-world Ethereum addresses use
capitalization as a checksum, and the server is using that too: align the hex of
an address with the hex its Keccak256 hash and upcase every letter where the
hash digit is 8 or higher (this is done automatically by `go-ethereum`; see
`scripts/exploit3` for a Python implementation).

Or you can skip all of this entirely.  One team had the great idea of throwing
addresses against their own binary and using `strace` to see what filenames
came out.

You can patch this by changing some bytes of the embedded HMAC key, but it's not
a complete fix, 'cause other teams can ask the static file server for the binary
itself and get your new key.  A better fix is to copy the binary and the static
files to a different directory and run it from there - the server always uses an
absolute path to the key storage directory, so this won't break anything.


## Bad Cryptography

You can also read a key by requesting it with a specially crafted password.

The server stores hashed passwords in `.hash` files alongside the `.json` files
that contain the key data.  But these files don't just contain hashes; they also
contain the messages that were hashed:

```go
message  := "\x19Ethereum Signed Message\n" + password
filedata := hash(message) + message
```

The server checks passwords with a "safe" constant-ish time comparison command
(see `safecomp_cmd` in `source/main.go`).  This computes the number of byte
differences between two files: the number of mismatched bytes plus any
difference in file length.

This would be safe if it was done in a function call, but it's not: it happens
in the "secure worker" process, and the number of differences is returned to the
server as an eight-bit process exit code.  So if you can guess a password that
results in exactly 256 mismatches, the server will think it was a match!

The `.hash` files always start with a hash. That's 64 random-ish hex characters,
so you should expect about `64 * 1/16 = 4` matches, or `64 - 4 = 60` mismatches.
The constant string will always match, so you can ignore it.  Then you can use
your password to cause the remaining `256 - 60 = 196` mismatches; most of these
will come from the length difference, but it's also important to include some
randomness so you can keep retrying; eventually, you'll get it right and the
server will send you the key.

You can patch this by having `safecomp_cmd` use `|` instead of `+` to "count"
mismatches, but you'd also need to change the length difference calculation to
make the comparison perfectly secure.

Alternatively, you could patch `hashpass_cmd` to return only the hash; then the
existing `safecomp_cmd` would be fine, as there could be at most 64 mismatches.


## Command Injection

Finally, you can read any key you want with command injection.

For "convenience", the server allows version numbers to be serialized either as
numbers or as strings (see `source/strnum.go`); internally, they're stored as
`string`s.  So a version number can actually be any arbitrary string.  When used
to retrieve keys (`readdata_cmd` in `source/main.go`), though, version numbers
are always read from as `int`s.

You might think this would simply result in a parse error (and it does), but the
really bad part happens afterward: the version number is passed via `stdin`, and
that isn't cleaned up when a process panics.  Instead, it gets read by the
"secure worker" parent process.  And that's an Ash shell!

In order to get to the `readdata_cmd`, you need to pass a password check, but
that's easy: just create a key normally.  Then use that address and password
with an invalid version number: one non-numeric character to kill `readdata_cmd`
followed by whatever shell code you want.

You still have to know the filename you want to read, but it's a lot easier here
than in the path traversal attack 'cause you have a full shell.  The "secure
worker" has globbing turned off, but you can `set +f` it back on and use globs.
Or you can use `find -iname *.[hash].vN.json` to avoid dealing with the prefix
and capitalization entirely.  You can even echo into `./keys.ch readdata` and
have the binary do the work for you!

This is the trickiest flaw to patch.  The ideal patch would be to store version
numbers internally as `int`s, but this would require a lot of changes. Next best
would be to have the `strnum` unmarshaller make sure that version strings were
numeric, but that's still a big change compared to the other patches.

The simplest binary patch is to take advantage of the fact that the service
scripts only ever send version numbers as strings, and skip the string parsing
step entirely - this technically removes functionality, but that functionality
is never tested.


## Patch Notes

Don't like binary patching?  Do it in a proxy!

- Throw away GET requests to the `append` directory.
- Throw away POST requests with suspiciously long passwords.
- Throw away POST requests with non-numeric version numbers.

It's not as classy, but it's a _lot_ simpler.
