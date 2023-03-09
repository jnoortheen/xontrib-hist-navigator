# xontrib-hist-navigator

Fish-shell like `prevd` and `nextd` for [xonsh](https://github.com/xonsh/xonsh/) with keyboard shortcuts

# Installation

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

# Usage

1. Add the following to your `.py` xontrib loading config and `import` it in your xonsh run control file (`~/.xonshrc` or `~/.config/rc.xsh`):
```py
from xonsh.xontribs 	import xontribs_load
from xonsh.built_ins	import XSH
envx = XSH.env

xontribs = [ "hist_navigator", # Initializes hist_navigator (fish-shell-like dir history navigation)
 # your other xontribs
]
# ↓ optional configuration variables (use `False` to disable a keybind)
if 'hist_navigator' in xontribs: # configure xontrib only if it's loaded
  # config var                 value  |default|alt_cmd¦ comment
  envx["XSH_HISTNAV_KEY_PREV"] = "⎇←"  #|['escape','left' ]|False¦ Move to the previous working directory
  envx["XSH_HISTNAV_KEY_NEXT"] = "⎇→"  #|['escape','right']|False¦ Move to the next working directory in the history (if 'prevd' was used)
  envx["XSH_HISTNAV_KEY_UP"]   = "⎇↑"  #|['escape','up'   ]|False¦ Move to the parent directory
  # run to see the allowed list for ↑: from prompt_toolkit.keys import ALL_KEYS; print(ALL_KEYS)
  # Alt is also supported as either of: a- ⎇ ⌥ (converted to a prefix 'escape')
  # Control symbols are also supported as either of: ⎈ ⌃
  # Arrow key symbols are also supported as either of: ▼▲◀▶ ↓↑←→
  envx["XSH_HISTNAV_EMPTY_PROMPT"] = False #|True|False¦ Keybinds only work in an empty prompt

xontribs_load(xontribs) # actually load all xontribs in the list
```

2. Or just add this to your xonsh run control file
```xsh
xontrib load hist_navigator
# configure like in the example above, but replace envx['VAR'] with $VAR
$XSH_HISTNAV_KEY_PREV	= "⎇←" # ...
```

# Overview

- it keeps track of `cd` usage per session
- Shortcuts

| command | description                                                        | shortcut          |
| ------- | ------------------------------------------------------------------ | ----------------- |
| prevd   | move to previous working directory                                 | Alt + Left Arrow  |
| nextd   | move to next working directory in the history (if `prevd` is used) | Alt + Right Arrow |
| listd   | list cd history                                                    |                   |
| cd ..   | move to parent directory                                           | Alt + Up Arrow    |

# Release

```sh
poetry version
poetry publish
```
