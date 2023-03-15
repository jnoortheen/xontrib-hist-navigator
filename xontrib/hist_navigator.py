import re
from prompt_toolkit.filters import Condition
from xonsh.built_ins import XSH
from prompt_toolkit.keys import ALL_KEYS

envx = XSH.env or {}

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
    from xonsh.ptk_shell.key_bindings import carriage_return

    b = event.current_buffer
    b.insert_text(text)
    carriage_return(b, event.cli)


@XSH.builtins.events.on_ptk_create  # noqa
def custom_keybindings(bindings, **_):
    from prompt_toolkit.key_binding.key_bindings import _parse_key

    re_despace = re.compile(r'\s', re.IGNORECASE)

    _default_keys = {
        "X_HISTNAV_KEY_PREV" : ['escape','left' ],
        "X_HISTNAV_KEY_NEXT" : ['escape','right'],
        "X_HISTNAV_KEY_UP"   : ['escape','up'   ],
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
        if   key_user == None:     # doesn't exist       → use default
            if type(key_def) == list:
                return bind_add(*key_def, filter=filter)
            else:
                return bind_add( key_def, filter=filter)
        elif key_user == False:    # exists and disabled → don't bind
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
            print_color("{BLUE}xontrib-hist_navigator:{RESET} your "+key_user_var+" '{BLUE}"+str(key_user)+"{RESET}' is {RED}invalid{RESET}; "+\
              "using the default '{BLUE}"+str(key_def)+"{RESET}'; run ↓ to see the allowed list\nfrom prompt_toolkit.keys import ALL_KEYS; print(ALL_KEYS)")
            if type(key_def) == list:
                return bind_add(*key_def, filter=filter)
            else:
                return bind_add( key_def, filter=filter)

    @handler("X_HISTNAV_KEY_PREV", filter=cmd_empty_prompt)
    def bind_prevd(event):
        """Equivalent to typing `prevd<enter>`"""
        insert_text(event, "prevd")

    @handler("X_HISTNAV_KEY_NEXT", filter=cmd_empty_prompt)
    def bind_nextd(event):
        """Equivalent to typing `nextd<enter>`"""
        insert_text(event, "nextd")

    @handler("X_HISTNAV_KEY_UP", filter=cmd_empty_prompt)
    def execute_version(event):
        """cd to parent directory"""
        insert_text(event, "cd ..")


__all__ = ("XSH_DIRS_HISTORY",)
