import subprocess
import os


def toRealPath(base_path, filename):
    # Get rid of \r
    filename = filename.replace("\r", "")

    # Trim whitespace
    filename = filename.strip()

    # Trim the leading dot if it exists
    if filename.startswith("."):
        filename = filename[1:]

    # Trim leading slash if it exists
    if filename.startswith("/"):
        filename = filename[1:]

    return os.path.join(base_path, filename)


def trimCodeBlocks(text):
    return text.strip("```")


def format_file(file):
    try:
        subprocess.run(
            ["prettier", "--write", file],
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        error_message = (
            f"An error occurred while formatting {file} with Prettier:\n"
            f"Output: {e.output}\n"
            f"Error: {e.stderr}\n"
        )
        return error_message

    return None


def format_code_with_line_numbers(code):
    lines = code.split('\n')
    max_line_number_length = len(str(len(lines)))
    formatted_lines = []

    for index, line in enumerate(lines, start=1):
        line_number = f"{index:>{max_line_number_length}}"
        formatted_line = f"{line_number} | {line}"
        formatted_lines.append(formatted_line)

    formatted_code = '```\n' + '\n'.join(formatted_lines) + '\n```'
    return formatted_code
