# pkg-update-checker

A script that sends a [Pushover] notification when a FreeBSD package update is found.

![pushover-demo]

## Usage

```
pkg-update-checker.py
  -p, --pkg=PKG           package name
  -j, --jail=JAIL         jail name
  -t, --po-token=TOKEN    Pushover token
  -u, --po-user=USER      Pushover user
  -l, --po-lock-dir=DIR   directory for Pushover lockfiles
                          (to suppress notifications)
```

### Example

```
python3 pkg_update_checker.py --jail unifi --pkg unifi5 --po-token <TOKEN> --po-user <USER>
```

[Pushover]: https://pushover.net/
[pushover-demo]: pushover-demo.png