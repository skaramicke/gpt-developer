from lib.parser import parse_commands


def test_parser():
    print('Test 1: Check if log commands are parsed correctly')
    message = '''
Hello, this is a log message.

read file1.html, file2.html
'''
    commands = parse_commands(message)
    assert commands[0]['command'] == 'log' and commands[0]['contents'].strip(
    ) == 'Hello, this is a log message.'
    assert commands[1]['command'] == 'read' and commands[1]['arg'] == 'file1.html, file2.html'

    print('Test 2: Check if missing arguments for multiline commands are detected')
    message = '''
write  Delimiter
This should fail due to a missing filename.
Delimiter
'''
    try:
        commands = parse_commands(message)
        assert False, "Exception not raised for missing argument in multiline command"
    except Exception as e:
        assert str(e) == "Missing argument for command `write`."

    print('Test 3: Check if unclosed delimiter is detected')
    message = '''
write file1.html Delimiter
Content without closing delimiter.
'''
    try:
        commands = parse_commands(message)
        assert False, "Exception not raised for unclosed delimiter"
    except Exception as e:
        # Assert that e contains the correct error message
        assert str(e).startswith(
            "Command `write` was not closed with delimiter `Delimiter`.")

    print('Test 4: Check if multiline commands are parsed correctly')
    message = '''
write file1.html Delimiter
This is the content of the file.
Delimiter
'''
    commands = parse_commands(message)
    assert commands[0]['command'] == 'write' and commands[0]['arg'] == 'file1.html' and commands[0]['contents'].strip(
    ) == 'This is the content of the file.'

    print('Test 5: Check if singleline commands are parsed correctly')
    message = '''commit This is a commit message'''
    commands = parse_commands(message)
    assert commands[0]['command'] == 'commit' and commands[0]['arg'] == 'This is a commit message'

    print('Test 6: Issuing only a read command should work just fine')
    message = "read file1.html"

    commands = parse_commands(message)
    assert commands[0]['command'] == 'read' and commands[0]['arg'] == 'file1.html'

    print('Test 7: Test the commit command')

    message = "commit This is a commit message"
    commands = parse_commands(message)
    assert commands[0]['command'] == 'commit' and commands[0]['arg'] == 'This is a commit message'

    print("All tests passed")


if __name__ == '__main__':
    test_parser()
