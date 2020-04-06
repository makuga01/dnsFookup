# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (at least tries to).


## [2.0.0] - 6. April 2020

### Added

- Config
  - config is now loaded from config.yaml in root of project

- DNS
  - CNAME and AAAA records are now supported!
  - Multithreading on DNS server
  - TCP is now supported too
  - In config.yaml you can set `domain` for which the dns server will work
  - Ability to set `use_failure_ip` in config.yaml to false -> dns server returns nxdomain if queried bin doesn't exist
  - Ability to set `use_fail_ns` to true -> so when somebody request domain that is not 'gel0.space' or whatever you set, dns server can return ns record with specified ip

- Settings panel
  - Delete all data functionality
  - Change password functionality
  - Copy JWT token button

- In `/mybins`
  - A brief overview of rebinding flow
  - Copy domain name button
  - Delete bin button
  - Pagination

- In `/dnsbin`
  - Support for CNAME and AAAA
  - "4ever" can be supplied to the repeat field now
  - When submitted there is functionality to copy generated subdomain

- "Support me" page ❤️ - If you get a huuuuge bounty using my tool why not donate few bucks

- Bottom bar buttons
  - Star project on github
  - Contact me
  - About me
  - Support me

- Added basic (and buggy) app vulnerable to TOCTOU/DNS rebinding ssrf so you can try it at home :D

### Changed
- D4RK mode is here and it's permanent (for now)
  - true 1337 h4xx0rs don't need light mode anyways

- DNS
  - DNS server now runs in [dnslib](https://pypi.org/project/dnslib/)

- Login
  - Weird bug where you were logged but actually weren't should be fixed now

- API
  - json inputs are now validated with [jsonschema](https://pypi.org/project/jsonschema/)
