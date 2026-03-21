from email.mime.base import MIMEBase
from email import encoders
import os
import sys

def attach_file(message, filepath):

    part = MIMEBase("application", "octet-stream")

    with open(filepath, "rb") as f:
        part.set_payload(f.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f'attachment; filename="{filepath}"'
    )

    message.attach(part)

def base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)