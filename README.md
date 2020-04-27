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
- `nextd` -> move to previous working directory (`Alt + Left Arrow`)
- `prevd` -> move to next working directory in the history (`Alt + Right Arrow`), if `prevd` is used.
