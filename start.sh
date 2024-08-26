#!/bin/bash
gunicorn --timeout 120 --log-level debug -w 4 -b 0.0.0.0:5002 app:app --daemon --access-logfile access.log --error-logfile error.log
