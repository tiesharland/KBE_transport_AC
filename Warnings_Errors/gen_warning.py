
def generate_warning(warning_header, msg):
    """
    This function generates a warning dialog box
    :param warning_header: The text to be shown on the dialog box header
    :param msg: the message to be shown in dialog box
    :return: None as it is a GUI operation
    """
    # tkinter is the GUI library used by the ParaPy desktop GUI
    from tkinter import Tk, messagebox

    # initialization
    window = Tk()
    window.withdraw()

    # generates message box and waits for user to close it
    messagebox.showwarning(warning_header, msg)

    # close the message window, terminate the associated process
    window.deiconify()
    window.destroy()
    window.quit()
