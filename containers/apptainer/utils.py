import os


def verify_root():
    return os.geteuid() == 0


def check_root():
    assert (
        os.geteuid() == 0
    ), "You need to have root privileges to run these scripts.\n\
        Please try executing on a developer machine with root:\n\
        $ sudo su -\n\
        $ pytest containers"
