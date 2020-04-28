from prompt_toolkit.application import get_app
from prompt_toolkit.filters import Condition

try:
    from xonsh.ptk.key_bindings import carriage_return
except ImportError:
    from xonsh.ptk_shell.key_bindings import carriage_return


class _DirsHistory:
    def __init__(self):
        self.history = []
        self.cursor = -1
        self.moved = False

    def add(self, old: str, new: str):
        if not self.moved:
            if not self.history:
                self.history.append(old)
            self.history.append(new)
            self.cursor = len(self.history) - 1

    def prev(self):
        self.cursor = max(self.cursor - 1, 0)
        self._move()

    def next(self):
        self.cursor = min(self.cursor + 1, len(self.history) - 1)
        self._move()

    def _move(self):
        if self.history:
            self.moved = True
            item = self.history[self.cursor]
            # @formatter:off
            cd @(item)  # noqa
            # @formatter:on
            self.moved = False

    def __repr__(self):
        if self.history:
            return "<Dirs:{}-{}>".format(
                self.history[: self.cursor + 1], self.history[self.cursor + 1:]
            )
        return "<Dirs: >"


XSH_DIRS_HISTORY = _DirsHistory()


@events.on_chdir  # noqa
def _add_to_history(olddir, newdir, **kwargs):
    XSH_DIRS_HISTORY.add(olddir, newdir)


def _prevd():
    XSH_DIRS_HISTORY.prev()


aliases["prevd"] = _prevd  # noqa


def _nextd():
    XSH_DIRS_HISTORY.next()


aliases["nextd"] = _nextd  # noqa


@events.on_ptk_create  # noqa
def custom_keybindings(bindings, **kw):
    handler = bindings.add

    @Condition
    def cmd_empty_prompt():
        app = get_app()
        return (
                not app.current_buffer.text
                and app.current_buffer.document.is_cursor_at_the_end
        )

    def insert_text(event, text):
        b = event.current_buffer
        b.insert_text(text)
        carriage_return(b, event.cli)

    @handler("escape", "left", filter=cmd_empty_prompt)
    def bind_prevd(event):
        insert_text(event, "prevd")

    @handler("escape", "right", filter=cmd_empty_prompt)
    def bind_nextd(event):
        insert_text(event, "nextd")

__all__ = ('XSH_DIRS_HISTORY', )
