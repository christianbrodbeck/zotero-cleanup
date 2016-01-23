# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>


def ask(prompt, options=('y', 'n'), default=None):
    """
    Parameters
    ----------
    prompt : str
        Prompt to ask the user (without options).
    options : tuple of str
        Options of valid responses.

    Returns
    -------
    response : str
        User response, lowercase.
    """
    prompt += " [%s] " % '/'.join(options)
    options_lower = [o.lower() for o in options]
    while True:
        choice = raw_input(prompt).lower()
        if default is not None and choice == '':
            return default
        elif choice in options_lower:
            return choice
        else:
            print("Invalid response.")
