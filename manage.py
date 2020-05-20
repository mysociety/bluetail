#!/usr/bin/env python
import os
import sys

try:
    os.environ.pop("DJANGO_SETTINGS_MODULE")
except Exception:
    pass

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
