from ...constants import SHELL_STATUS_RUN


def debug(args):
    if len(args) > 0:
        from ...logger import log
        import logging
        if 'enable' in args:
            log.setLevel(logging.DEBUG)
            print("Enable debug")
        elif 'disable' in args:
            log.setLevel(logging.INFO)
            print("Disable debug")
    else:
        print("Must specify : debug enable / debug disable")
    return SHELL_STATUS_RUN
