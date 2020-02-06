from gsc_utils import metadata, utils

welcome_message = """
You can find the source for Google Search Console Utilities at {0}
"""
welcome_message = welcome_message.format(metadata.source)
utils.print_err(welcome_message)
