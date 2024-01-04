# Console
A Ren'Py tool that emulates a terminal / command line.

![image](https://github.com/Elckarow/Console/assets/101005497/82ac96c8-842d-4d09-95e4-2da55885cbd7)

# Documantation
***Every variables and functions described below are defined in the `console` namespace.***
-

- `HISTORY_LENGTH = 20`

How many console entries we save.

- `enter_transition = Dissolve(0.3)`

The default transition used when showing the console.

- `exit_transition = Dissolve(0.3)`

The default transition used when hiding the console.

- `def show(transition=enter_transition, delay=0.4)`

Shows the console. Pauses for `delay` seconds after (*delay=None* will wait for user input, while *delay=-1* won't pause at all).

- `def hide(transition=enter_transition, delay=0.4)`

Hides the console.

- `def input(text, delay=-1, cps=30, output_entry=None)`

Adds an input `text` to the console, which is displayed with a cps of `cps` (*None* means instant display). If `output_entry` is not *None*, it is either a string, or *True* (which will take `text` for value). Will add the string as an output after the before function returns.

![image](https://github.com/Elckarow/Console/assets/101005497/635694c2-4283-4124-96e5-4ff490a98fbb)

- `def output(text, delay=None, cps=None)`

Adds an output to the console.

![image](https://github.com/Elckarow/Console/assets/101005497/66d4d507-0a5f-4ffa-965f-b3e711397ef4)

- `def interact(delay=-1, input_entry=None, empty=True, **kwargs)`

Prompts the player for an input, which is then returned. If `empty` is true, the string won't be returned as long as it is empty. This also takes the following parameters; `length`, `allow`, `exclude`, `prefix`, `suffix`, `multiline`, `copypaste` and `mask`; as described for the `input` screen language statement.

- `def clean_history()`

Pops the console history until its length is less than `HISTORY_LENGTH`.

- `def clear_history()`

Clears the console.
