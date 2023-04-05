import re

header_pattern = re.compile("^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@$")

patch_doc = """
Unified Format Patch
Each hunk shows one area where the source string and the target differs.
Unified format hunks look like this:
@@ from-text-line-numbers to-text-line-numbers @@
 line-from-either-text
 line-from-either-text...
If a hunk contains just one line, only its start line number appears. Otherwise its line numbers look like ‘start,count’. An empty hunk is considered to start at the line that follows the hunk.
If a hunk and its context contain two or more lines, its line numbers look like ‘start,count’. Otherwise only its end line number appears. An empty hunk is considered to end at the line that precedes the hunk.
The lines common to both strings begin with a space character. The lines that actually differ between the two strings have one of the following indicator characters in the left print column:
‘+’ A line was added here to the first string.
‘-’ A line was removed here from the first string.
Example:
@@ -1,7 +1,6 @@
-The Way that can be told of is not the eternal Way;
-The name that can be named is not the eternal name.
 The Nameless is the origin of Heaven and Earth;
-The Named is the mother of all things.
+The named is the mother of all things.
+
 Therefore let there always be non-being,
   so we may see their subtlety,
 And let there always be being,
@@ -9,3 +8,6 @@
 The two are the same,
 But after they are produced,
   they have different names.
+They both may be called deep and profound.
+Deeper and more profound,
+The door of all subtleties!
"""


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


if __name__ == '__main__':
    sample_text = """The Way that can be told of is not the eternal Way;
The name that can be named is not the eternal name.
The Nameless is the origin of Heaven and Earth;
The Named is the mother of all things.
Therefore let there always be non-being,
  so we may see their subtlety,
And let there always be being,
  so we may see their outcome.
The two are the same,
But after they are produced,
  they have different names."""
    sample_patch = """@@ -1,7 +1,6 @@
-The Way that can be told of is not the eternal Way;
-The name that can be named is not the eternal name.
 The Nameless is the origin of Heaven and Earth;
-The Named is the mother of all things.
+The named is the mother of all things.
+
 Therefore let there always be non-being,
   so we may see their subtlety,
 And let there always be being,
@@ -9,3 +8,6 @@
 The two are the same,
 But after they are produced,
   they have different names.
+They both may be called deep and profound.
+Deeper and more profound,
+The door of all subtleties!
"""
    print(apply_patch(sample_text, sample_patch))
