#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""pkg-update-checker: This script checks if a specified FreeBSD package has an
update available, and sends a notification via Pushover to the specified
Pushover user in the event that a newer version of the package is found.
"""

import getopt
import os
import requests
import subprocess
import sys


def print_help_message():
  print("""pkg-update-checker.py
    -p, --pkg=PKG           package name
    -j, --jail=JAIL         jail name
    -t, --po-token=TOKEN    Pushover token
    -u, --po-user=USER      Pushover user
    -l, --po-lock-dir=DIR   directory for Pushover lockfiles
                            (to suppress notifications)
    """)


def get_args(argv):
  pkg_name = ""
  jail_name = ""
  po_token = ""
  po_user = ""
  po_lock_dir = ""

  try:
    opts, args = getopt.getopt(
        argv, "hj:p:t:u:l:", ["help", "jail=", "pkg=", "po-token=", "po-user=", "po-lock-dir="])
  except getopt.GetoptError:
    print("invalid args")
    print_help_message()
    sys.exit(2)

  for opt, arg in opts:
    if opt in ("-h", "--help"):
      print_help_message()
      sys.exit()
    elif opt in ("-j", "--jail"):
      jail_name = arg
    elif opt in ("-p", "--pkg"):
      pkg_name = arg
    elif opt in ("-t", "--po-token"):
      po_token = arg
    elif opt in ("-u", "--po-user"):
      po_user = arg
    elif opt in ("-l", "--po-lock-dir"):
      po_lock_dir = arg

  if pkg_name == "" or po_token == "" or po_user == "":
    print("missing or invalid args")
    print_help_message()
    sys.exit(2)

  return pkg_name, jail_name, po_token, po_user, po_lock_dir


def get_cmd_output_or_exit(cmd):
  cmd_status, cmd_output = subprocess.getstatusoutput(cmd)
  if cmd_status != 0:
    print(cmd_output)
    print("ERROR running command \"" + cmd + "\"")
    sys.exit(cmd_status)
  return cmd_output


def pkg_has_new_version(pkg_cmd, pkg_name):
  pkg_version_cmd = pkg_cmd + " version --remote --exact " + pkg_name
  pkg_version_output = get_cmd_output_or_exit(pkg_version_cmd)
  return pkg_version_output.endswith("<")


def get_new_pkg_version(pkg_cmd, pkg_name):
  pkg_search_cmd = pkg_cmd + " search --quiet " + pkg_name
  pkg_search_output = get_cmd_output_or_exit(pkg_search_cmd)
  return pkg_search_output.split("-").pop()


def send_pushover_notification(token, user, title, message):
  print("sending a pushover notification... ", end="")
  req = requests.post("https://api.pushover.net/1/messages.json", data={
      "token": token, "user": user, "title": title, "message": message
  })
  success = (req.status_code == 200)
  if success:
    print("success")
  else:
    print("failure")
  return success


def main(argv):
  pkg_name, jail_name, po_token, po_user, po_lock_dir = get_args(argv)

  # use an empty "lock" file to only send one Pushover notification
  po_lock_file = po_lock_dir + pkg_name + "_has_update"

  # check if there is a new version of pkg_name (in jail jail_name, if provided)
  pkg_cmd = "pkg"
  if jail_name:
    pkg_cmd += " --jail " + jail_name
  if pkg_has_new_version(pkg_cmd, pkg_name):
    print("a new version of the specified package was found")

    # get the version number of the updated package
    pkg_version = get_new_pkg_version(pkg_cmd, pkg_name)

    # send one notification (via Pushover) per update
    if not os.path.isfile(po_lock_file):
      po_title = pkg_name + " Update Available!"
      po_message = "Version " + pkg_version + \
          " of FreeBSD package " + pkg_name + " is available."
      if send_pushover_notification(po_token, po_user, po_title, po_message):
        # disallow multiple successful notifications
        open(po_lock_file, 'a').close()
        print("notification suppression lockfile created")
    else:
      print("lockfile found -- suppressing pushover notification")

  else:
    print("no updates available for the specified package")
    if os.path.isfile(po_lock_file):
      os.remove(po_lock_file)
      print("notification suppression lockfile removed")


if __name__ == "__main__":
  main(sys.argv[1:])
