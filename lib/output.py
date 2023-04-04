def print_github_log_message(role, text):
    if role.lower() == 'assistant':
        prefix = '[Assistant]'
        color = '\033[1;34m'  # Blue
    elif role.lower() == 'user':
        prefix = '[User]'
        color = '\033[1;32m'  # Green
    else:
        raise ValueError(
            "Invalid role. Role must be either 'assistant' or 'user'.")

    reset_color = '\033[0m'  # Reset color
    separator = '-' * 80

    print(f"{color}{separator}\n{prefix}\n{text}\n{separator}{reset_color}")
