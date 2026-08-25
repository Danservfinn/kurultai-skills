# Manual verification checklist

Run each assertion from a clean shell. `<image>` is any locally available image (e.g. `alpine:latest`).

1. **Signature appears on stderr, not in journald.** Run `docker run --rm -v "/tmp/session:t1":/root <image> true 2>err.log; echo $?` (after `mkdir -p "/tmp/session:t1"`). Assert: exit code is 125 and `grep -i "invalid mode" err.log` prints `Error response from daemon: invalid mode: /root`. Also assert `journalctl -u docker --since "5 min ago" | grep -i "invalid mode"` returns nothing — confirming the skill correctly directs you to stderr, not daemon logs.

2. **`--mount` fix works with a pre-created colon source.** Run `mkdir -p "/tmp/session:t1"` then `docker run --rm --mount type=bind,source="/tmp/session:t1",target=/root <image> true; echo $?`. Assert: exit code 0. (Without the `mkdir -p`, this same command fails with "bind source path does not exist" — `--mount` does not auto-create sources.)

3. **Colon-free control succeeds with `-v`.** Run `mkdir -p /tmp/session-t1 && docker run --rm -v /tmp/session-t1:/root <image> true; echo $?`. Assert: exit code 0.

4. **Repo-agnostic search step runs anywhere.** From any repository checkout (not the Hermes repo), run the step-3 greps with `<repo>` set to that checkout. Assert: the commands exit without "No such file or directory" errors (grep simply returns no matches or matches from that repo).

5. **Health-check step is conditional.** Confirm the skill's step-1 instructions only invoke `<health-cmd>` when the application provides one; running the step on a host without `hermes` installed must not be required.

6. **Regression test exists after the fix.** After applying the patch, run the project's test suite filtered for the new test (e.g. `python -m pytest -k colon`). Assert: the colon-identifier test passes and, if the pre-patch code is checked out, the same test fails.