import re
import typing
import threading
from pathlib import Path
from prompt_toolkit.filters import Condition
from xonsh.built_ins import XSH
from prompt_toolkit.keys import ALL_KEYS
from xonsh.style_tools import partial_color_tokenize
from prompt_toolkit.formatted_text import PygmentsTokens
from xonsh.ptk_shell.shell import tokenize_ansi
from xonsh.tools import print_color

envx = XSH.env or {}
cdx = XSH.aliases["cd"]

class _DirsHistory:
    def __init__(self):
        self.history = []
        self.cursor = -1
        self.moved = False

    def _append(self, item: str):
        if self.history and item == self.history[-1]:
            return  # do not add same item twice in the stack
        self.history.append(item)

    def add(self, old: str, new: str):
        if not self.moved:
            if not self.history:
                self._append(old)
            self._append(new)
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
            _cd_inline(item)
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


def _p_msg_fmt(s):
    return tokenize_ansi(PygmentsTokens(partial_color_tokenize(XSH.shell.shell.prompt_formatter(s)))) # noqa

def _update_prompt(): # force-update all 3 prompts (if exist) to new values
    # Helpful when xontrib changes prompt vars in the background and
    # doesn't want to wait for the next prompt cycle
    shellx = XSH.shell.shell
    shellx.prompt_formatter.fields.reset() # reset fields cache
    if prompt_l := envx['PROMPT']:
        prompt_l = prompt_l() if callable(prompt_l) else prompt_l
        shellx.prompter.message        = _p_msg_fmt(prompt_l)
    if prompt_r := envx['RIGHT_PROMPT']:
        prompt_r = prompt_r() if callable(prompt_r) else prompt_r
        shellx.prompter.rprompt        = _p_msg_fmt(prompt_r)
    if prompt_b := envx['BOTTOM_TOOLBAR']:
        prompt_b = prompt_b() if callable(prompt_b) else prompt_b
        shellx.prompter.bottom_toolbar = _p_msg_fmt(prompt_b)
    shellx.prompter.app.invalidate()      # send signal that prompt needs update


@Condition
def cmd_empty_prompt():
    app = XSH.shell.prompter.app
    return (
        not app.current_buffer.text and app.current_buffer.document.is_cursor_at_the_end
    )


@Condition
def key_always():
    """Always activate key binding"""
    return True

def insert_text(event, text):
    from xonsh.ptk_shell.key_bindings import carriage_return

    b = event.current_buffer
    b.insert_text(text)
    carriage_return(b, event.cli)


def _cd_inline(path: typing.Optional[typing.AnyStr] = None) -> None:
    """Change dir without creating a new prompt line, updating existing instead"""

    if path is None:
        args = []
    elif isinstance(path, bytes):
        args = [path.decode("utf-8")]
    elif isinstance(path, str):
        args = [path]
    if         path and \
      not Path(path).is_dir():
        return # do nothing is target is not a Dir
    _, exc, _ = cdx(args)
    if exc is not None:
        raise Exception(exc)
    else:
        t = threading.Thread(target=_update_prompt, args=())
        t.start()


@XSH.builtins.events.on_ptk_create  # noqa
def custom_keybindings(bindings, **_):
    from prompt_toolkit.key_binding.key_bindings import _parse_key

    re_despace = re.compile(r'\s', re.IGNORECASE)

    _default_keys = {
        "XSH_HISTNAV_KEY_PREV" : ['escape','left' ],
        "XSH_HISTNAV_KEY_NEXT" : ['escape','right'],
        "XSH_HISTNAV_KEY_UP"   : ['escape','up'   ],
    }

    _key_symb = {
        '⎈':'c-'  ,'⌃':'c-'   ,
        '▼':'down' ,'↓':'down' ,
        '▲':'up'   ,'↑':'up'   ,
        '◀':'left' ,'←':'left' ,
        '▶':'right','→':'right',
    }
    _alts = ['a-','⌥','⎇']

    def handler(key_user_var, filter):
        def skip(func):
          pass

        if envx.get('SHELL_TYPE') in ["prompt_toolkit", "prompt_toolkit2"]:
            bind_add = bindings.add
        else:
            bind_add = bindings.registry.add_binding

        key_user = envx.get(     key_user_var, None)
        key_def  = _default_keys[key_user_var]
        if   key_user is None:     # doesn't exist       → use default
            if type(key_def) == list:
                return bind_add(*key_def, filter=filter)
            else:
                return bind_add( key_def, filter=filter)
        elif key_user is False:    # exists and disabled → don't bind
            return skip
        elif type(key_user) == str:# remove whitespace
            key_user = re_despace.sub('',key_user)

        for k,v in _key_symb.items(): # replace symbols
            if k in key_user: # replace other keys
                key_user = key_user.replace(k,v)
                break
        for alt in _alts:
            if alt in key_user: # replace alt with an ⎋ sequence of keys
                key_user = ['escape', key_user.replace(alt,'')]
                break

        if   type(key_user) == str  and\
             key_user in ALL_KEYS: # exists and   valid  → use it
            return bind_add(key_user, filter=filter)
        elif type(key_user) == list and\
            all(k in ALL_KEYS or _parse_key(k) for k in key_user):
            return bind_add(*key_user, filter=filter)
        else:                      # exists and invalid  → use default
            print_color("{BLUE}xontrib-hist_navigator:{RESET} your "+\
                key_user_var+" '{BLUE}"+str(key_user)+\
                "{RESET}' is {RED}invalid{RESET}; "+\
              "using the default '{BLUE}"+str(key_def)+\
              "{RESET}'; run ↓ to see the allowed list\n"+\
              "from prompt_toolkit.keys import ALL_KEYS; print(ALL_KEYS)")
            if type(key_def) == list:
                return bind_add(*key_def, filter=filter)
            else:
                return bind_add( key_def, filter=filter)

    if envx.get("XSH_HISTNAV_EMPTY_PROMPT", ""):
        _filter = cmd_empty_prompt
    else:
        _filter = key_always

    @handler("XSH_HISTNAV_KEY_PREV", filter=_filter)
    def bind_prevd(event):
        """cd to `prevd`"""
        prevd()

    @handler("XSH_HISTNAV_KEY_NEXT", filter=_filter)
    def bind_nextd(event):
        """cd to `nextd`"""
        nextd()

    @handler("XSH_HISTNAV_KEY_UP", filter=_filter)
    def execute_version(event):
        """cd to parent directory"""
        _cd_inline('..')


__all__ = ("XSH_DIRS_HISTORY",)
