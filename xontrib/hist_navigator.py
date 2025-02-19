from configparser import ConfigParser

from prompt_toolkit.filters import Condition
from xonsh.built_ins import XSH


def is_truthy(s: str) -> bool:
    return ConfigParser.BOOLEAN_STATES.get(s.lower(), False)


class _DirsHistory:
    def __init__(self):
        self.history = []
        self.cursor = -1
        self.moved = False

    def _append(self, item: str):
        if self.history and item == self.history[-1]:
            return  # do not add same item twice in the stack
        self.history.append(item)

    @property
    def cursor_left(self):
        return max(self.cursor - 1, 0)

    @property
    def cursor_right(self):
        return min(self.cursor + 1, len(self.history) - 1)

    def add(self, old: str, new: str):
        if not self.moved:
            if not self.history:
                self._append(old)
            else:
                if new == self.history[self.cursor_left]:
                    return self.prev()
                if new == self.history[self.cursor_right]:
                    return self.next()

                should_truncate = XSH.env.get("XONTRIB_HIST_NAVIGATOR_TRUNCATE", "0")
                if is_truthy(should_truncate):
                    self.history = self.history[: self.cursor + 1]
            self._append(new)
            self.cursor = len(self.history) - 1

    def prev(self):
        self.cursor = self.cursor_left
        self._move()

    def next(self):
        self.cursor = self.cursor_right
        self._move()

    def _move(self):
        if self.history:
            self.moved = True
            item = self.history[self.cursor]
            XSH.subproc_captured_stdout(["cd", item])
            self.moved = False

    def __repr__(self):
        if self.history:
            return "<Dirs:{}-{}>".format(
                self.history[: self.cursor + 1], self.history[self.cursor + 1 :]
            )
        return "<Dirs: >"


XSH_DIRS_HISTORY = _DirsHistory()


@XSH.builtins.events.on_chdir  # noqa
def _add_to_history(olddir, newdir, **kwargs):
    XSH_DIRS_HISTORY.add(olddir, newdir)


def add_alias(func):
    XSH.aliases[func.__name__] = func
    return func


@add_alias
def prevd():
    """Move to previous directory in the cd-history"""
    XSH_DIRS_HISTORY.prev()


@add_alias
def nextd():
    """Move to next directory in the cd-history"""
    XSH_DIRS_HISTORY.next()


@add_alias
def listd():
    """List directories in cd-history"""
    print(XSH_DIRS_HISTORY.history)


@Condition
def cmd_empty_prompt():
    app = XSH.shell.prompter.app
    return (
        not app.current_buffer.text and app.current_buffer.document.is_cursor_at_the_end
    )


def insert_text(event, text):
    from xonsh.shells.ptk_shell.key_bindings import carriage_return

    b = event.current_buffer
    b.insert_text(text)
    carriage_return(b, event.cli)


@XSH.builtins.events.on_ptk_create  # noqa
def custom_keybindings(bindings, **_):
    handler = bindings.add

    @handler("escape", "left", filter=cmd_empty_prompt)
    def bind_prevd(event):
        """Equivalent to typing `prevd<enter>`"""
        insert_text(event, "prevd")

    @handler("escape", "right", filter=cmd_empty_prompt)
    def bind_nextd(event):
        """Equivalent to typing `nextd<enter>`"""
        insert_text(event, "nextd")

    @handler("escape", "up", filter=cmd_empty_prompt)
    def execute_version(event):
        """cd to parent directory"""
        insert_text(event, "cd ..")


__all__ = ("XSH_DIRS_HISTORY",)
