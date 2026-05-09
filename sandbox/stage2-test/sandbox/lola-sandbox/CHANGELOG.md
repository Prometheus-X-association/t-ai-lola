## Changelog file for lola-sandbox
## Be careful to keep the same format for all release version.
## The continous integration generate extract the changelog automatically

# Version 1.0.4
- [**features**]:
  - Add option `--no-lrs` to disable the necessity of LRS server. Data of your scenario
  should be stored locally

# Version 1.0.3
- **[Fix]**
  - Improve error messages (#17, #16)

# Version 1.0.2
- [**Fix**]:
  - Docker check version (#15)

# Version 1.0.1
- [**features**]:
  - Rename pip installation name from `sandbox` to `lola-sandbox` (#14)
  - Add binary for Linux available in the package registry (#9)
  - Add `--version` option 
- [**Fix**]:
  - Docker check before running `--help` (#13)
