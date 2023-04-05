#!/bin/bash

echo "Enter issue text"

read issue_text
issue_number=1

python gpt.py "$OPENAI_API_SECRET" "$issue_number" "$issue_text" ./test_code