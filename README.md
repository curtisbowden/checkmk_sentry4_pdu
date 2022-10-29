# Checkmk extension for Sentry4 PDU status, outlets and environment sensors based on Sentry4-MIB

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/curtisbowden/checkmk_sentry4_pdu?label=version&logo=git&sort=semver)

![build](https://github.com/curtisbowden/checkmk_sentry4_pdu/workflows/build/badge.svg)
![flake8](https://github.com/curtisbowden/checkmk_sentry4_pdu/workflows/Lint/badge.svg)
![pytest](https://github.com/curtisbowden/checkmk_sentry4_pdu/workflows/pytest/badge.svg)

## Description

- `sentry4_pdu_status` discovers and checks pdu metadata and unit status
  - unit ID
  - unit Name
  - unit Serial Number
  - unit Model
  - unit Type
  - unit Status

-

## Development

For the best development experience use [VSCode](https://code.visualstudio.com/) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This maps your workspace into a checkmk docker container giving you access to the python environment and libraries the installed extension has.

## CheckMK

Below are a few cmk cli examples that can be useful when developing a cmk plugin

```
# Service scan for exmaple.host
cmk --verbose --perfdata --debug example.host

# Clear prevous then detect plugins for sentry4_pdu_status
cmk --verbose --perfdata --debug -II --detect-plugins=sentry4_pdu_status example.host

# Check discovery for emaple.host
cmk --verbose --perfdata --check-discovery example.host

# Run isis_adjacency plugin on example.host
cmk --verbose --perfdata --plugins=sentry4_pdu_status example.host
```


## Directories

The following directories in this repo are getting mapped into the Checkmk site.

* `agents`, `checkman`, `checks`, `doc`, `inventory`, `notifications`, `pnp-templates`, `web` are mapped into `local/share/check_mk/`
* `agent_based` is mapped to `local/lib/check_mk/base/plugins/agent_based`
* `nagios_plugins` is mapped to `local/lib/nagios/plugins`

## Continuous integration
### Local

To build the package hit `Crtl`+`Shift`+`B` to execute the build task in VSCode.

`pytest` can be executed from the terminal or the test ui.

### Github Workflow

The provided Github Workflows run `pytest` and `flake8` in the same checkmk docker conatiner as vscode.
