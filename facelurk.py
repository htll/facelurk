#!/usr/bin/env python

import re
import sys
import time
from robobrowser import RoboBrowser

if len(sys.argv) != 4:
    print("Usage: {} <email> <pass> <target ID>".format(sys.argv[0]))
    sys.exit()
email, pas, target = sys.argv[1:4]
try:
    target = "profile.php?id={}".format(int(target))
except ValueError:
    pass
if not "?" in target:
    target += "?dontmindme=" # fix for custom IDs

browser = RoboBrowser()
browser.open("https://facebook.com")

form = browser.get_form(id="login_form")
form["email"] = email
form["pass"] = pas
browser.submit_form(form)

def get_friends():
    root = browser.find(id="root")
    h3 = root.find("h3")
    if not h3: return []
    friends = h3.findNext("div")
    if not friends: return []
    return friends.find_all("a", href=re.compile("fref=fr_tab"))

def next_page(reg=re.compile("friends.*&startindex=")):
    link = browser.get_link("See More Friends")
    if not link:
        return False
    browser.follow_link(link)
    time.sleep(0.2) # just to be sure
    return True

print("starting to listen...")
browser.open("https://m.facebook.com/{}&v=friends".format(target))
while len(get_friends()) < 10:
    browser.open("https://m.facebook.com/{}&v=friends".format(target))
    time.sleep(2)
print("more than ten friends, proceeding to get list")

count = 0
with open("friends", "w") as file:
    for friend in get_friends():
        file.write("{} {}\n".format(friend["href"], friend.text))
        count += 1
    while next_page():
        for friend in get_friends():
            file.write("{} {}\n".format(friend["href"], friend.text))
            file.flush() # just to be sure
            count += 1

print("got {} friends".format(count))
