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
| prevd   | move to previous working directory                                 | Alt + Left Arrow  |
| nextd   | move to next working directory in the history (if `prevd` is used) | Alt + Right Arrow |
| listd   | list cd history                                                    |                   |
| cd ..   | move to parent directory                                           | Alt + Up Arrow    |


# Traversal behavior

By default, all cd history is kept. Let's look at an example. Let's open
a new shell:

```sh
❯
```

Now when we change the directory, it's added to the history along with
the previous directory where we were (the user's home directory):

```sh
❯ cd BASE
❯ listd
['~', '~/BASE']
```

Let's descend further down:

```sh
❯ cd sub
❯ listd
['~', '~/BASE', '~/BASE/sub']
```

So far, so obvious. Now, when we use `prevd`, you'll see that the history
stays intact:

```sh
❯ prevd
❯ pwd
~/BASE
❯ listd
['~', '~/BASE', '~/BASE/sub']
```

This allows you to use `nextd` to go back and forth:

```sh
❯ nextd
❯ pwd
~/BASE/sub
❯ listd
['~', '~/BASE', '~/BASE/sub']
❯ prevd
❯ pwd
~/BASE
❯ listd
['~', '~/BASE', '~/BASE/sub']
```

Now, if you change the directory entirely after a `prevd`, the entire
previous history is still kept:

```sh
❯ pwd
~/BASE
❯ listd
['~', '~/BASE', '~/BASE/sub']
❯ cd /tmp
❯ listd
['~', '~/BASE', '~/BASE/sub', '/tmp']
```

This means that issuing `prevd` now will actually return to `~/BASE/sub`
and not to `~/BASE` which was the last seen previous directory.
This is by design to allow you to quickly traverse previously visited
directories using keyboard shortcuts.

If you would rather have the history truncated, so that `prevd` always
takes you to the directory you were in just before, set the following
environment variable in your xonshrc:

```xsh
$XONTRIB_HIST_NAVIGATOR_TRUNCATE="true"
```

In this case the last example would behave differently:

```sh
❯ pwd
~/BASE
❯ listd
['~', '~/BASE', '~/BASE/sub']
❯ cd /tmp
❯ listd
['~', '~/BASE', '/tmp']
```

As you can see `~/BASE/sub` was dropped from history because it wasn't
the last visited directory at the time of changing the directory to
`/tmp`.


# Release

```sh
semantic-release version && semantic-release publish
```
