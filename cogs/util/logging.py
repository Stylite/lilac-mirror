#!/usr/bin/env python

"""Logger used to log messages to console."""

class Logger:
    def __init__(self):
        self.logs = []

    def get_log(self, count):
        if count > len(self.logs):
            return '\n'.join(self.logs)
        else:
            to_return = self.logs[-1*count:]
            return '\n'.join(to_return)

    def write(self, data):
        self.logs.append(data.strip())

    def log(self, tag, message):
        print(f'[{tag}] {message}')
