import random
from locust import FastHttpUser, HttpUser, between, task
from pyquery import PyQuery
import csv
import os

csvfile = open(os.path.join(os.path.dirname(__file__), "userlist.csv"))
iter = csv.reader(csvfile)
wait_time = between(1, 5)

courseId = 14

print(f"Loaded {len(list(iter))} users from userlist.csv")

class MoodleBaseUser(HttpUser):
    def on_start(self):
        # start by waiting so that the simulated users
        # won't all arrive at the same time
        self.wait()
        # assume all users arrive at the index page
        self.index_page()

    def loginAsNextUser(self):
        try:
            username, password = next(iter)
        except StopIteration:
            # go back to start of the file once its been exhausted
            csvfile.seek(0, 0)
            username, password = next(iter)

        return self.loginAs(username, password)

    def loginAs(self, username, password):
        r = self.client.get('/login/index.php')

        # Parse the login page to extract the logintoken
        d = PyQuery(r.text)
        logintoken = d('input[name=logintoken]').val()
        r = self.client.post('/login/index.php', {
            "username": username,
            "password": password,
            "logintoken": logintoken,
        });

        if r.status_code != 200:
            print(f"Login failed for user {username} with status code {r.status_code}")
        else:
            print(f"Logged in as {username}")

        return r


    @task
    def index_page(self):
        print(f"Visiting index page")
        r = self.client.get("/")
        if (r.status_code != 200):
            print(f"Failed to load index page with status code {r.status_code}")
            print("r text:", r.text)

    @task
    def toggleBlock(self):
        print(f"Logging in as next user")
        r = self.loginAsNextUser()
        r = self.client.post('/api/rest/v2/user/current/preferences/drawer-open-block', json={"value": True})
        print(f"Toggled block returned status code {r.status_code}")
        r = self.client.post('/api/rest/v2/user/current/preferences/drawer-open-block', json={"value": False})

    @task
    def viewCourse(self):
        print(f"Logging in as next user")
        r = self.loginAsNextUser()
        r = self.client.get(f'/course/view.php?id={courseId}')
        print(f"View course returned status code {r.status_code}")
