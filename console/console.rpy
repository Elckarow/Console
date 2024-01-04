init python:
    def hyperlink_functions_style(name):
        """
        Hyperlink functions but the style `name` is used.

        `name`: str
            The style to use.
        """
        style_object = getattr(style, name)
        return (lambda target: style_object,) + style.default.hyperlink_functions[1:]

    def pause(time=None):
        if time is None:
            ui.saybehavior(afm=" ")
            ui.interact(mouse='pause', type="pause", roll_forward=None)
            return
        if time <= 0: return
        renpy.pause(time)

default console.history = [ ]
default console._current_entry = None
default console._typing_indicator = True

init python in console:
    from renpy import store
    from store import _window_hide, pause, __, Dissolve, basestring, ui

    HISTORY_LENGTH = 20

    enter_transition = Dissolve(0.3)
    exit_transition = Dissolve(0.3)

    def show(transition=enter_transition, delay=0.4):
        """
        Shows the console.
        """
        if renpy.get_screen("console") is None:
            renpy.show_screen("console")
            if transition is not None:
                renpy.with_statement(transition)
            pause(delay)
    
    def hide(transition=exit_transition, delay=0.4):
        """
        Hides the console.
        """
        if renpy.get_screen("console") is not None:
            renpy.hide_screen("console")
            if transition is not None:
                renpy.with_statement(transition)
            pause(delay)
    
    class _Entry(object):
        def __init__(self, entry, cps):
            if not isinstance(entry, basestring): raise ValueError(f"expected str, got {entry.__class__.__name__}")
            self.entry = entry
            self.cps = cps
    
    class Input(_Entry): pass
    class Output(_Entry): pass

    class Interact(object):
        def __init__(self, length=None, allow=None, exclude=None, prefix="", suffix="", multiline=True, mask=None, copypaste=True):
            self.value = ""

            self.length = length
            self.allow = allow
            self.exclude = exclude
            self.prefix = prefix
            self.suffix = suffix
            self.multiline = multiline
            self.mask = mask
            self.copypaste = copypaste

    _yadjustment = renpy.display.behavior.Adjustment()
    
    def input(text, delay=-1, cps=30, output_entry=None):
        """
        Adds an input to the console.

        `text`: str
            The entry's text.
        
        `delay`: int | None
            Passed to `pause` after the input's done.
        
        `cps`: int
            The cps used.
        
        `output_entry`: None | str | True
            If not `None`, creates an output at the end of the input. If `True` is passed, `text` is used as value.
        """
        input_entry = Input(text, cps)
        _entry(input_entry, delay)

        if output_entry is not None:
            if output_entry is True:
                output_entry = text
            elif not isinstance(output_entry, basestring):
                raise TypeError("output_entry expected None, str or True, got %r" % output_entry)
            
            output(output_entry, delay=-1, cps=None)
            
    def output(text, delay=None, cps=None):
        """
        Adds an output to the console.

        `text`, `delay` and `cps` are the same as the `input` function.
        """
        output_entry = Output(text, cps)
        _entry(output_entry, delay)
    
    def interact(delay=-1, input_entry=None, empty=True, **kwargs):
        """
        Prompts the player for an input, which is then returned.

        This takes the following parameters;
        `length`, `allow`, `exclude`, `prefix`, `suffix`, `multiline`, `copypaste` and `mask`;
        as described for the `input` screen language statement.

        Also accepts `delay`, `empty` and `input_entry` (which is just like `output_entry` described in `console.input`, but with an input).
        """
        return _interact(Interact(**kwargs), delay, input_entry, empty)

    def clean_history():
        """
        Pops the history until its length is < than HISTORY_LENGTH.
        """
        while len(history) >= HISTORY_LENGTH:
            history.pop(0)

    def clear_history():
        """
        Clears the history.
        """
        history.clear()
    
    def _get_time(entry):
        return (len(renpy.filter_text_tags(renpy.substitute(entry.entry), allow=())) + 1) / entry.cps

    def _entry_coroutine():
        global _current_entry, _typing_indicator

        window_auto = store._window_auto
        _window_hide()
        _current_entry = yield
        _yadjustment.value = float("inf")

        delay = yield
        store._window_auto = window_auto
        _current_entry = None
        _yadjustment.value = float("inf")
        pause(delay)
        _typing_indicator = True

        yield None
    
    def _entry(entry, delay=None):
        global _typing_indicator
        cr = _entry_coroutine()
        cr.send(None)

        history.append(entry)
        clean_history()   
        cr.send(entry)   

        if entry.cps is not None:
            _current_entry = entry
            _typing_indicator = False
            pause(_get_time(entry))

        cr.send(delay)
    
    def _interact(entry, delay=None, input_entry=None, empty=True):
        cr = _entry_coroutine()
        cr.send(None)
        cr.send(entry)

        while True:
            rv = ui.interact()
            if rv or empty:
                break

        if input_entry is not None:
            if input_entry is True:
                input_entry = rv
            elif not isinstance(input_entry, basestring):
                raise TypeError("input_entry expected None, str or True, got %r" % input_entry)

            input(input_entry, delay=-1, cps=None)

        cr.send(delay)
        return rv

screen console():
    style_prefix "console"

    frame:
        viewport:
            draggable True
            mousewheel True
            yadjustment console._yadjustment
            yinitial 1.0

            vbox:
                for entry in console.history:
                    if entry is not console._current_entry:
                        if isinstance(entry, console.Input):
                            use _console_input():
                                text entry.entry
                        elif isinstance(entry, console.Output):
                            text entry.entry
                                
                    else:
                        if isinstance(entry, console.Input):
                            use _console_input():
                                add renpy.display.layout.AdjustTimes(
                                        Text(
                                            entry.entry,
                                            style="console_text",
                                            slow_cps=entry.cps,
                                        ),
                                        None,
                                        None
                                    )
                        elif isinstance(entry, console.Output):
                            add renpy.display.layout.AdjustTimes(
                                    Text(
                                        entry.entry,
                                        style="console_text",
                                        slow_cps=entry.cps,
                                    ),
                                    None,
                                    None
                                )
                
                if isinstance(console._current_entry, console.Interact):
                    use _console_input():
                        input:
                            value FieldInputValue(console._current_entry, "value", returnable=True)
                            length console._current_entry.length
                            mask console._current_entry.mask
                            copypaste console._current_entry.copypaste
                            multiline console._current_entry.multiline
                            allow console._current_entry.allow
                            exclude console._current_entry.exclude
                            prefix console._current_entry.prefix
                            suffix console._current_entry.suffix
                            caret_blink False

                else:
                    if console._typing_indicator:
                        use _console_input():
                            add "_console_typing_indicator"

screen _console_input():
    style_prefix "console"

    hbox:
        text ">>> " yoffset 1

        transclude

image _console_typing_indicator:
    Text("_", style="console_text", bold=True)
    subpixel True
    block:
        alpha 1.0
        pause 0.6
        alpha 0.0
        pause 0.6
        repeat

style console_viewport is empty
style console_vbox is empty:
    spacing 12
style console_hbox is empty

style console_frame is empty:
    background "#333333bf"
    xysize (480, 180)
    padding (7, 10, 20, 7)

style console_text is empty:
    font "console/F25_Bank_Printer.ttf"
    color "#fff"
    size 18
    line_leading 1
    outlines []
    hyperlink_functions hyperlink_functions_style("console_hyperlink")

style console_hyperlink is console_text:
    underline True

style console_input is console_text:
    caret "_console_typing_indicator"
