# xontrib-hist-navigator

Fish-shell like `prevd` and `nextd` for [xonsh](https://github.com/xonsh/xonsh/) with keyboard shortcuts

# Usage

- install using pip
```sh
pip install xontrib-hist-navigator
```

- or xpip (that is installed alongside xonsh)

```sh
xpip install xontrib-hist-navigator
```

- add to list of xontribs loaded.

```sh
xontrib load hist_navigator
```

# Overview

- it keeps track of `cd` usage per session
- Shortcuts

| command | description                                                        | shortcut          |
| ------- | ------------------------------------------------------------------ | ----------------- |
| nextd   | move to previous working directory                                 | Alt + Left Arrow  |
| prevd   | move to next working directory in the history (if `prevd` is used) | Alt + Right Arrow |
| listd   | list cd history                                                    |                   |
| cd ..   | move to parent directory                                           | Alt + Up Arrow    |

# Release

```sh
poetry version
poetry publish
```
