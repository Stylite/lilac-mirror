#!/usr/bin/env python

"""Logger used to log messages to console."""

class Logger:
    def __init__(self):
        self.logs = []

    def get_log(self, count):
        if count > len(self.logs):
			print(repr(''.join(self.logs)))
            return ''.join(self.logs)
        else:
            to_return = self.logs[-1*count:]
            return ''.join(to_return)

    def write(self, data):
        self.logs.append(data.strip() + '\n')

    def log(self, tag, message):
        print(f'[{tag}] {message}')
