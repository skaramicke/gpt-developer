import re

header_pattern = re.compile("^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@$")


def apply_patch(source, patch, revert=False):
    """
    Apply unified diff patch to string s to recover newer string.
    If revert is True, treat s as the newer string, recover older string.
    """
    source = source.splitlines(True)
    patch_lines = patch.splitlines(True)
    target = ''
    i = source_line = 0
    (midx, sign) = (1, '+') if not revert else (3, '-')
    while i < len(patch_lines) and patch_lines[i].startswith(("---", "+++")):
        i += 1  # skip header lines
    while i < len(patch_lines):
        match = header_pattern.match(patch_lines[i])
        if not match:
            raise Exception("Cannot process diff")
        i += 1
        l = int(match.group(midx))-1 + (match.group(midx+1) == '0')
        target += ''.join(source[source_line:l])
        source_line = l
        while i < len(patch_lines) and patch_lines[i][0] != '@':
            if i+1 < len(patch_lines) and patch_lines[i+1][0] == '\\':
                line = patch_lines[i][:-1]
                i += 2
            else:
                line = patch_lines[i]
                i += 1
            if len(line) > 0:
                if line[0] == sign or line[0] == ' ':
                    target += line[1:]
                source_line += (line[0] != sign)
    target += ''.join(source[source_line:])
    return target
