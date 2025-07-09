# CHANGELOG


## v3.1.1 (2025-07-09)

### Bug Fixes

- Fix tests and uvx invocation error, and update GH workflows
  ([`d3f87a8`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/d3f87a82e48bbc733fe9912ce4b30c55d1302e0e))


## v3.1.0 (2025-07-09)

### Features

- Add support for loading PagerDuty API token from .env file
  ([`6692db0`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/6692db0732ec6e0b392939f1d1c82521e4524246))

- Add python-dotenv dependency to pyproject.toml - Update client.py to automatically load .env file
  on import - Update README.md to document .env file usage as recommended option - Add comprehensive
  tests for .env file loading functionality - Update CHANGELOG.md to document new feature - Add
  .DS_Store to .gitignore

The server now automatically loads environment variables from .env file if present, while existing
  environment variables take precedence.


## v3.0.0 (2025-06-25)

### Chores

- Expose 'earliest' param in list_oncalls API
  ([`7508128`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/75081283933e5d0118914b624db989571c6a6c34))

- Llms are dumb
  ([`91ccebe`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/91ccebecbe5d323f4afd2cfd02cb99095977cbd8))

- Make user context object human-readable
  ([`2b91a9c`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/2b91a9c104f6abcdbf122802433ae8e452785c63))

### Documentation

- Documentation fixes
  ([`a282e30`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/a282e30c2f4f783a497dd095e29b2da119a3e9c5))

- Spaghetti cleanup
  ([`3bb3182`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/3bb31825b2eda9e31370edf7b5d4b0d2b11fb853))

### Features

- Incorporating upstream bchanges
  ([`c1380cc`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/c1380cce8ba77fc4c255d5a7be0b6a5b993258b2))


## v2.2.0 (2025-03-31)

### Features

- Implement list_related_incidents and list_users_oncall APIs
  ([`74bad51`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/74bad51e882f74ae2afcf74ea57ae944d0590f9c))

housekeeping: improve tests and make sure all list_ methods respect limit param


## v2.1.0 (2025-03-28)

### Features

- Expose list_past_incidents API
  ([`49059a1`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/49059a1cddd3c6603292b3d59e9e66df6f1af099))


## v2.0.0 (2025-03-28)

### Features

- Actual initial release
  ([`9b3426a`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/9b3426a7d5273d4fef04659bb859642d4e621865))

BREAKING CHANGE: go straight to 2.0.0 to make Pypi happy

### Breaking Changes

- Go straight to 2.0.0 to make Pypi happy


## v1.0.0 (2025-03-28)

### Features

- Initial release
  ([`8871b39`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/8871b39982c4a648e7181cd2daf5e27e49d227a0))

BREAKING CHANGE: clean start, skipping 1.0.0 to make Pypi happy

### Breaking Changes

- Clean start, skipping 1.0.0 to make Pypi happy


## v0.1.0 (2025-03-28)

### Features

- Initial release
  ([`658a4c5`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/658a4c55ea81ace2b9f9d23ae5cc983fa04ddc02))
