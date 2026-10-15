# ipa-interbank — iCTF 2006

**Competition:** iCTF 2006 "The Hillbilly Bank" (December 8, 2006, UCSB Frank Hall)
**Category:** web / ruby
**Format:** Attack-defense service
**Port:** 3000 (HTTP, mongrel)

## Overview

iPal ("inter-pal") is the Hillbilly Bank's currency exchange service — a Ruby on Rails 1.x
web application run via mongrel. Teams competed to attack and defend this service.
Users register, deposit RSA-signed checks issued by the central bank, and withdraw
funds (converted to various currencies) to an IBAN address.

## Architecture

```
http://<host>:3000/                       — welcome page
http://<host>:3000/session/signup         — register
http://<host>:3000/session/login          — log in
http://<host>:3000/user/show              — profile
http://<host>:3000/user/show_deposits     — view deposits
http://<host>:3000/deposit/new            — deposit a check
http://<host>:3000/deposit/destroy/<id>   — withdraw (transfer out)
http://<host>:3000/admin/                 — admin interface
```

Runs as user `ipa` via:
```
/usr/bin/mongrel_rails start -e production -d -u ipa --group ipa
```

Database: MySQL (`ipal_production`, username: `ipal`, password: `citieffe`)

## Vulnerability

`DepositController#create` (`app/controllers/deposit_controller.rb`) passes
`params[:check_id]` directly into a shell command:

```ruby
ccheck = IO.popen("/usr/bin/ccheck #{params[:check_id]}", "r")
```

A length check (`!= 172`) is enforced, but shell metacharacters within a
172-character string allow command injection. For example, embedding `;cat flag;`
padded to the required length executes arbitrary commands on the server.

## Files

| Path | Description |
|------|-------------|
| `src/app/controllers/deposit_controller.rb` | Deposit/withdrawal handler (**vulnerable**) |
| `src/app/controllers/session_controller.rb` | Login/signup |
| `src/app/controllers/user_controller.rb` | User profile |
| `src/app/controllers/admin_controller.rb` | Admin CRUD |
| `src/app/controllers/currency_controller.rb` | Currency management |
| `src/app/models/user.rb` | User model (auth) |
| `src/app/models/deposit.rb` | Deposit model |
| `src/app/models/currency.rb` | Currency model |
| `src/app/views/` | ERB templates |
| `src/config/database.yml` | DB config (credentials) |
| `src/config/routes.rb` | URL routing |
| `src/db/schema.rb` | DB schema |
| `src/db/ipal.sql` | SQL dump from CTF VM |
| `src/lib/authenticated_system.rb` | Authentication library |
| `src/Rakefile` | Build tasks |
| `src/README` | Original Rails README |
| `src/init_ipa` | `/etc/init.d/ipa` service init script |

## Notes

- Source extracted from the CTF VM (Ubuntu Dapper, VMware VMDK) via `qemu-img` + `debugfs`.
- The `ccheck` binary (`/usr/bin/ccheck`) verifies RSA-signed 172-character base64 checks
  issued by the Hillbilly Central Bank.
- The scoring script (`ipa_botscript.py`) in `../hillbilly-bank/src/` exercises this service.
