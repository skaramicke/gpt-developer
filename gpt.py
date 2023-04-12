# python gpt.py ${{ inputs.openai_api_key }} ${{ inputs.issue_number }} ${{ inputs.issue_text }} ${{ inputs.path }}

import os
import sys
import openai
from lib.output import print_github_log_message, set_output
from lib.parser import documentation, parse_commands
from lib.text import toRealPath, trimCodeBlocks, format_file, format_code_with_line_numbers

openai.api_key = sys.argv[1]
issue_number = sys.argv[2]
issue_text = sys.argv[3]
path = sys.argv[4]

# List complete filenames recursively
files = []
for root, dirs, filenames in os.walk(path):
    for filename in filenames:
        # skip .git and .github directories
        if ".git" in root or ".github" in root:
            continue

        # remove the path variable from the filename
        files.append(os.path.join(root, filename).replace(path, "."))

files = ", ".join(files)

commands_doc = documentation()

prompt = f"""Issue #{issue_number}: {issue_text}
{commands_doc}
Existing files: {files}
You are interacting with software. Solve the issue detailed above using the commands documented above. You use commands to `read`, `write`, `remove` files in the code and then `comment` on the issue or `commit` the changes. `exit` to stop.
You need to use the commands. The text you write is being parsed by a custom software that executes the commands. There's no human on the other end.
"""

messages = [
    {"role": "user", "content": prompt},
]
print_github_log_message("user", prompt)

while True:

    completions = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
    )

    response = completions["choices"][0]["message"]["content"]

    print_github_log_message("assistant", response)
    messages.append({"role": "assistant", "content": response})

    user_message = ''

    try:
        commands = parse_commands(response)

        if len([command for command in commands if command["command"] != "log"]) == 0:
            user_message += f"No commands detected in ```{response}```. You can ONLY use commands. The text you write is being parsed by a custom software that executes the commands. There's no human on the other end. If you are done processing the issue, use the command `exit`.\n{commands_doc}"

        for command in commands:
            if command["command"] == "exit":
                break

            # Print all commands except log, since the AI is not aware of the log command.
            if command["command"] != "log":
                user_message += f'# {command["command"]}\n'

            if command["command"] == "comment":
                set_output("comment_message", command["contents"])
                user_message += f'comment stored: {command["contents"]}'

            if command["command"] == "commit":
                set_output("commit_message", command["arg"])
                user_message += f'commit message stored: {command["arg"]}'

            if command["command"] == "read":
                files = command["arg"].split(",")

                file_contents = ""
                for filename in files:
                    file_path = toRealPath(path, filename)
                    with open(file_path, "r") as f:
                        code = format_code_with_line_numbers(f.read())
                        file_contents += f"`{filename}`:\n{code}\n"

                user_message += f"{file_contents}\n"

            if command["command"] == "write":

                filename = command["arg"]
                file_path = toRealPath(path, filename)

                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, "w") as f:
                    f.write(command["contents"])

                formatting_errors = format_file(file_path)

                with open(file_path, "r") as f:
                    code = format_code_with_line_numbers(f.read())
                    if formatting_errors:
                        user_message += f"wrote file `{filename}`:\n{code}\nPlease fix the formatting errors:\n{formatting_errors}\n"
                    else:
                        user_message += f"wrote file `{filename}`:\n{code}\n"

            if command["command"] == "remove":
                files = command["arg"].split(",")
                for filename in files:
                    file_path = toRealPath(path, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        user_message += f"removed {filename}\n"
                    else:
                        user_message += f"{filename} does not exist\n"

    except Exception as e:
        # Create an error string where any occurrence of `path` has been replaced with a period
        error = str(e).replace(path, ".")
        user_message += f"error: {error}"
        pass

    user_message = user_message.strip()
    if user_message != "":
        print_github_log_message("user", user_message)
        messages.append({"role": "user", "content": user_message})
    else:
        break


print("done")
