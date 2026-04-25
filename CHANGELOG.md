# CHANGELOG


## v3.1.2 (2026-04-25)

### Bug Fixes

- Trigger PyPI publish only on actual releases
  ([`d17571c`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/d17571c26409d8cb71cc77731d982f4e9cc9b870))

publish.yml used workflow_run on "Automated Release" completion, which fires on every push to main
  -- including no-op runs where python-semantic-release finds nothing to release. This caused
  spurious uploads of already-published versions (400 File already exists).

Switching to the release:published event so the workflow only runs when a GitHub Release is actually
  created.

### Chores

- **deps**: Bump hatch from 1.14.1 to 1.16.5
  ([`1252895`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/1252895e2ca68c234c4e35d779770c9de42a25d7))

Bumps [hatch](https://github.com/pypa/hatch) from 1.14.1 to 1.16.5. - [Release
  notes](https://github.com/pypa/hatch/releases) -
  [Commits](https://github.com/pypa/hatch/compare/hatch-v1.14.1...hatch-v1.16.5)

--- updated-dependencies: - dependency-name: hatch dependency-version: 1.16.5

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump pytest from 8.4.1 to 9.0.3
  ([`c4dac57`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/c4dac578c0be49d76cc2e2f4c6cd1070421acefa))

Bumps [pytest](https://github.com/pytest-dev/pytest) from 8.4.1 to 9.0.3. - [Release
  notes](https://github.com/pytest-dev/pytest/releases) -
  [Changelog](https://github.com/pytest-dev/pytest/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/pytest-dev/pytest/compare/8.4.1...9.0.3)

--- updated-dependencies: - dependency-name: pytest dependency-version: 9.0.3

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump ruff from 0.12.0 to 0.15.12
  ([`0acf822`](https://github.com/wpfleger96/pagerduty-mcp-server/commit/0acf82231579e37fa8718404ea2d4a7930043785))

Bumps [ruff](https://github.com/astral-sh/ruff) from 0.12.0 to 0.15.12. - [Release
  notes](https://github.com/astral-sh/ruff/releases) -
  [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/astral-sh/ruff/compare/0.12.0...0.15.12)

--- updated-dependencies: - dependency-name: ruff dependency-version: 0.15.12

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>


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
