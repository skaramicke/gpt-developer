# python gpt.py ${{ inputs.openai_api_key }} ${{ inputs.issue_number }} ${{ inputs.issue_text }} ${{ inputs.path }}

import os
import sys
import openai
from lib.output import print_github_log_message, set_output
from lib.parser import documentation, parse_commands
from lib.patch import apply_patch
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

", ".join(files)

commands_doc = documentation()

prompt = f"""Issue #{issue_number}: {issue_text}
{commands_doc}
files: {files}
instructions: use commands to `read`, `create`, `patch`, `remove` files and then `comment` on the issue or `commit` the changes. `exit` to stop.
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
            user_message += f"no commands found\n{commands_doc}"

        for command in commands:
            if command["command"] == "exit":
                break

            if command["command"] != "log":
                user_message += f'# {command["command"]}\n'

            if command["command"] == "log":
                print_github_log_message("assistant", command["contents"])

            if command["command"] == "comment":
                set_output("comment", command["contents"])
                user_message += f'comment stored: {command["contents"]}'

            if command["command"] == "commit":
                set_output("commit", command["contents"])
                user_message += f'commit message stored: {command["contents"]}'

            if command["command"] == "read":
                files = command["arg"].split(",")

                file_contents = ""
                for filename in files:
                    file_path = toRealPath(path, filename)
                    with open(file_path, "r") as f:
                        code = format_code_with_line_numbers(f.read())
                        file_contents += f"`{filename}`:\n{code}\n"

                user_message += f"{file_contents}\n"

            if command["command"] == "create":

                filename = command["arg"]
                file_path = toRealPath(path, filename)

                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, "w") as f:
                    f.write(command["contents"])

                format_file(file_path)

                with open(file_path, "r") as f:
                    code = format_code_with_line_numbers(f.read())
                    user_message += f"created file `{filename}`:\n{code}\n"

            if command["command"] == "patch":

                filename = command["arg"]
                file_path = toRealPath(path, filename)

                with open(file_path, "r") as f:
                    file_contents = f.read()
                    new_file_contents = apply_patch(
                        file_contents, command["contents"])
                    if new_file_contents == file_contents:
                        user_message = f"no changes to {filename}"
                    else:
                        with open(file_path, "w") as write_f:
                            write_f.write(new_file_contents)
                        format_file(file_path)
                        with open(file_path, "r") as formatted_f:
                            created_file_contents = formatted_f.read()
                            code = format_code_with_line_numbers(
                                created_file_contents)
                            user_message += f"patched {filename}. Result: {code}\n"

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
        user_message = f"error: {error}"
        pass

    user_message = user_message.strip()
    if user_message != "":
        print_github_log_message("user", user_message)
        messages.append({"role": "user", "content": user_message})
    else:
        break


print("done")
