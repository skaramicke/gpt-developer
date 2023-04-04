# python gpt.py ${{ inputs.openai_api_key }} ${{ inputs.issue_number }} ${{ inputs.issue_text }} ${{ inputs.path }}

import os
import sys
import openai
from lib.output import print_github_log_message, set_output
from lib.patch import apply_patch
from lib.text import toRealPath, trimCodeBlocks, format_files, format_code_with_line_numbers

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

commands = """commands:
  readfiles <comma separated list of file paths to view>
  patchfile <filename to change>\\n<patch with python diff_match_patch syntax>
  createfile <filename of new file>\\n<contents of new file>
  removefile <filename to remove>
  commit <message describing change in 'this commit will <message>' syntax>
  comment <write a comment on the issue, with all relevant information, since this conversation is not available in the issue>
If you think the issue is already resolved, use the comment command. Don't ever apologise or write any other such text. Only use commands, and never anything else. When you're done, use the commit command.
"""

prompt = f"""Issue #{issue_number}: {issue_text}
{commands}
files: {files}
instructions: use only a single command at a time. commands are case sensitive.
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

    try:
        debug_info = [path]

        user_message = ""

        if response.startswith("readfiles"):
            debug_info.append("readfiles")
            file_contents = ""
            files = response.split("readfiles ")[1].split(",")
            for filename in files:
                file_path = toRealPath(path, filename)
                debug_info.append(file_path)
                with open(file_path, "r") as f:
                    code = format_code_with_line_numbers(f.read())
                    file_contents += f"{filename}\n{code}\n"

            user_message = file_contents

        elif response.startswith("patchfile"):
            patch = response.split("patchfile ")[1]
            filename = patch.split("\n")[0]
            file_path = toRealPath(path, filename)
            patch = trimCodeBlocks("\n".join(patch.split("\n")[1:]))

            with open(file_path, "r") as f:
                file_contents = f.read()
                patched_file_contents = apply_patch(file_contents, patch)
                if patched_file_contents == file_contents:
                    user_message = f"no changes to {filename}"
                else:
                    with open(file_path, "w") as write_f:
                        write_f.write(patched_file_contents)
                    format_files(path)
                    with open(file_path, "r") as formatted_f:
                        created_file_contents = formatted_f.read()
                        code = format_code_with_line_numbers(
                            created_file_contents)
                        user_message = f"patched {filename}. Result: {code}"

        elif response.startswith("createfile"):
            filename = response.split("createfile ")[1].split("\n")[0]
            file_path = toRealPath(path, filename)
            file_contents = trimCodeBlocks("\n".join(response.split("\n")[1:]))

            with open(file_path, "w") as f:
                f.write(file_contents)
            format_files(path)
            with open(file_path, "r") as f:
                file_contents = f.read()
                code = format_code_with_line_numbers(file_contents)
                user_message = f"created {filename}. Result: {code}"

        elif response.startswith("removefile"):
            # Remove the filename relative to the path variable
            filename = response.split("removefile ")[1]
            file_path = toRealPath(path, filename)
            # check if the file exists
            if os.path.exists(file_path):
                # Remove the file
                os.remove(file_path)
                user_message = f"removed {filename}"
            else:
                user_message = f"{filename} does not exist"

        elif response.startswith("commit"):
            commit_message = response.split(
                "commit ")[1] + " - Closes #" + issue_number
            print_github_log_message(
                "assistant", f"commit message: {commit_message}")
            with open("commit-message.txt", "w") as f:
                f.write(commit_message)
            break

        elif response.startswith("comment"):
            exit_message = response.split("comment ")[1]
            with open("exit-message.txt", "w") as f:
                f.write(exit_message)
            break

        else:
            user_message = f"command not recognized/\n{commands}"

    except Exception as e:
        # Create an error string where any occurrence of `path` has been replaced with a period
        error = str(e).replace(path, ".")
        user_message = f"error: {error}"
        pass

    print_github_log_message("user", user_message)
    messages.append({"role": "user", "content": user_message})

print("done")
