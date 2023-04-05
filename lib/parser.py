import re

multiline_commands = {'create', 'patch', 'comment'}
singleline_commands = {'read', 'remove', 'commit', 'exit'}


def documentation():
    return '''Commands:
read: Read files
    read <comma separated filenames>
create: Create a file
    create <filename> <delimiter>
    <contents>
    <delimiter>
patch: Patch a file
    patch <filename> <delimiter>
    <unified diff patch>
    <delimiter>
remove: Remove files
    remove <comma separated filenames>
commit: Set the commit message
    commit <message>
comment: Set the comment message
    comment <delimiter>
    <message>
    <delimiter>
exit: Exit the program
    exit
Notes: Remember to use delimiters that don't occur in the content or patch blocks. @@ is a bad delimiter. If you use `<<EOF`, remember to print `<<EOF` at the end too, not just `EOF`.
    '''


def parse_commands(message):
    command_objects = []

    # Split the message into lines
    lines = message.split('\n')
    current_command = 'log'
    current_arg = ''
    current_contents = []
    command_end_delimiter = ''

    for line in lines:
        first_word = line.split(' ')[0]

        # Check if it's time to switch commands
        if command_end_delimiter == '' and first_word in multiline_commands:
            if current_command == 'log':
                text = ("\n".join(current_contents)).strip()
                if text != '':
                    command_objects.append({
                        'command': current_command,
                        'contents': text
                    })
            current_command = first_word
            arguments = line.split(' ')[1:]
            if len(arguments) > 1:
                # Strip whitespaces from arg
                current_arg = arguments[0].strip()
                if not current_arg:  # Check if arg is empty after stripping
                    raise Exception(
                        f"Missing argument for command `{current_command}`.")
                command_end_delimiter = ' '.join(arguments[1:]).strip()
            else:
                current_arg = ''
                command_end_delimiter = arguments[0].strip()
            current_contents = []
        elif (command_end_delimiter == '' and first_word in singleline_commands) or (command_end_delimiter != '' and first_word == command_end_delimiter):
            if current_command == 'log':
                text = ("\n".join(current_contents)).strip()
                if text != '':
                    command_objects.append({
                        'command': current_command,
                        'contents': text
                    })
            elif current_command in multiline_commands:
                command_objects.append({
                    'command': current_command,
                    'arg': current_arg,
                    'contents': "\n".join(current_contents)
                })
            if first_word != command_end_delimiter:
                command_objects.append({
                    'command': first_word,
                    # Strip whitespaces from arg
                    'arg': ' '.join(line.split(' ', 1)[1:]).strip(),
                })
            command_end_delimiter = ''
            current_command = 'log'
            current_contents = []
        else:
            current_contents.append(line)

    if command_end_delimiter != '':
        raise Exception(
            f"Command `{current_command}` was not closed with delimiter `{command_end_delimiter}`.")

    # Add any remaining log contents
    if current_contents:
        command_objects.append({
            'command': current_command,
            'arg': '',
            'contents': "\n".join(current_contents)
        })

    return command_objects


if __name__ == '__main__':
    print('This is a test script for the parser.py module.')
    # Example usage
    message = '''
Hello, and welcome

This is a log message that will appear in before any action is taken.

Now let's read some files...

read file1.html,file2.html

Now, create a new file with the following content.

We can set any delimiter we want, but it must be repeated at the end of the content.

create filename.html DelimiterWordThatCanBeAnything
Lorem ipsum dolor sit amet
DelimiterWordThatCanBeAnything
After that, remove the newly created file.
remove filename.html
Finally, set a commit message and a comment.
commit The commit message

comment delim
I wan to
exit
delim
exit
And that concludes our test.
'''

    print(documentation())

    commands = parse_commands(message)
    for command in commands:
        print(command)
