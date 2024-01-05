import os
import subprocess
from collections import defaultdict
from tqdm import tqdm

repo_path = "./"
valid_extensions = ['.kt', '.java', '.xml', '.py', '.js', '.html', '.css', '.kts', '.bat', '.sh', '.md', '.yml']
translation_files = ['strings.xml', 'fastlane', '/raw/', 'README.md']
ignored_files = ['.idea']


def count_lines_per_user(repo_path):
    # Change to the repository directory
    os.chdir(repo_path)

    # A dictionary to hold the line counts for each user
    user_line_count = defaultdict(int)

    # A dictionary to hold the number of lines of code
    user_code_line_count = defaultdict(int)

    # A diction to hold the number of lines of translations
    user_translation_line_count = defaultdict(int)

    # Getting a list of all files tracked by git
    files = subprocess.check_output("git ls-tree -r HEAD --name-only", shell=True).decode('utf-8').splitlines()

    # Iterating over each file and using git blame to find the author of each line
    with tqdm(total=len(files)) as pbar:
        for file in files:
            if not any([file.endswith(ext) for ext in valid_extensions]):
                pbar.update(1)
                continue

            if any([ignored in file for ignored in ignored_files]):
                pbar.update(1)
                continue

            is_translation = any([t in file for t in translation_files])

            try:
                # Getting the blame output for each file
                blame_output = subprocess.check_output(f"git blame --line-porcelain {file}", shell=True).decode('utf-8', errors='ignore')

                # Processing the output
                for line in blame_output.splitlines():
                    if line.startswith("author "):
                        author = line.split(" ", 1)[1]
                        user_line_count[author] += 1
                        if is_translation:
                            user_translation_line_count[author] += 1
                        else:
                            user_code_line_count[author] += 1
                
                pbar.update(1)

            except subprocess.CalledProcessError:
                # In case of an error (e.g., binary files), skip the file
                pbar.update(1)
                continue

    return user_line_count, user_code_line_count, user_translation_line_count

# Counting lines and printing the results
lines_by_user, code_lines, translation_lines = count_lines_per_user(repo_path)
total_lines = sum(lines_by_user.values())
total_code_lines = sum(code_lines.values())
total_translation_lines = sum(translation_lines.values())

rows = lines_by_user.items()
rows = sorted(rows, key=lambda x: x[1], reverse=True)

print(f"Total: {total_lines}, Code: {total_code_lines}, Translations: {total_translation_lines}")

for user, count in rows:
    total = count
    code = code_lines[user]
    translation = translation_lines[user]
    percent_of_total = round(count / total_lines * 100, 2)
    percent_of_code = round(code / total_code_lines * 100, 2)
    if total_translation_lines == 0:
        percent_of_translation = 0
    else:
        percent_of_translation = round(translation / total_translation_lines * 100, 2)
    print(f"{user}: {count} ({percent_of_total}%), Code: {code} ({percent_of_code}%), Translations: {translation} ({percent_of_translation}%)")