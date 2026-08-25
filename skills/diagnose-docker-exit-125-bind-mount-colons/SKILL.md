---
name: diagnose-docker-exit-125-bind-mount-colons
description: Diagnose and fix Docker container creation failures (exit status 125) caused by colon-containing identifiers in host paths passed via -v bind mounts
category: ops-automation
---

# Diagnose Docker exit 125 from colons in bind-mount host paths

## Goal

Identify when a `docker run` exit status 125 is caused by a colon in the host-side path of a `-v` bind mount (Docker parses the colon as a separator and rejects the mount with `invalid mode: <path>`), and fix the mount construction or path generation.

## Inputs

- The failing `docker run` command, its stderr, or the code that constructs it.
- The identifier scheme used to build host-side sandbox paths (e.g. `session:<session-id>`).
- The container image name used by the failing command.
- Optional: the application's health-check command (e.g. `hermes doctor`) if the application provides one.

## Steps

1. Rule out infrastructure causes: run `docker version` and `docker info`; confirm the image exists locally with `docker image inspect <image>`; run the application's health-check command if one exists. If any of these fail, stop — this skill does not apply.
2. Capture the signature error. Run the failing `docker run` command and capture its stderr: the signature is `Error response from daemon: invalid mode: <path>` printed by the docker CLI. Note which container-side path (e.g. `/root`, `/workspace`) Docker misinterprets as a mount mode. Do not rely on daemon logs (`journalctl -u docker`) — this error is returned via the API to the client, not written to journald on most hosts.
3. Locate the mount construction in the codebase. Find where `-v` arguments are generated and where the host-side path is built from an identifier. Use repo-agnostic searches (grep for `-v`, `--volume`, `volume=`, and the identifier prefix such as `session:`) rooted at the repository directory, not hardcoded paths from another codebase.
4. Reproduce minimally: create a host directory whose name contains a colon, then run `docker run -v <host-path-with-colon>:/root <image> true` and confirm exit status 125 with `invalid mode: /root`; confirm a colon-free path with the same command exits 0.
5. Fix by either (a) replacing the colon-containing logical identifier with a filesystem-safe slug for directory names while keeping the logical ID stored separately, or (b) switching generated mounts from `-v` short syntax to `--mount type=bind,source=...,target=...`, which handles colons in host paths safely. Note: `--mount` does not auto-create a missing source directory — create it first.
6. Add a regression test that exercises container creation when the session/task identifier contains a colon (e.g. build the mount args through the patched code path and assert the resulting `docker run` succeeds, or unit-test that the generated args use `--mount` or a slug).

## Outputs

- Root-cause diagnosis: colon in host path parsed as a `-v` separator, evidenced by `invalid mode: <path>` on the failing command's stderr.
- Patched mount construction or path-generation code.
- Regression test covering colon-containing identifiers.

## Failure modes

- Failing command's stderr not captured, so the `invalid mode` evidence is missing (daemon logs usually do not contain it).
- Other sources of exit 125 (image pull failure, name conflict, OCI runtime errors) mistaken for the colon issue — always confirm the `invalid mode` signature and the minimal repro before patching.
- Fixing only the display identifier while the raw colon ID is still used in path construction.
- Switching to `--mount` without pre-creating the source directory: `--mount` fails with "bind source path does not exist" where `-v` would auto-create it.

## Source

Discord thread `1485307775444844625/1540887579610714202` — "Docker backend fails with exit status 125 for Profile 2" (Hermes Agent v0.20.5, Docker 29.1.3), 2026-08-25.