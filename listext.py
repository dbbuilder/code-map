import os
from collections import defaultdict


def count_file_extensions(directory):
    """
    Counts the file extensions in the specified directory and its subdirectories.

    Args:
        directory (str): Path to the directory.

    Returns:
        dict: Dictionary with file extensions as keys and their counts as values.
    """
    extension_count = defaultdict(int)

    for root, _, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            extension_count[ext] += 1

    return extension_count


def main():
    directory = r"c:\devsv\forgpt"
    extension_count = count_file_extensions(directory)

    # Sort the extensions by count
    sorted_extensions = sorted(
        extension_count.items(), key=lambda item: item[1], reverse=True
    )

    # Print the results
    print("File extension counts (sorted by number of files):")
    for ext, count in sorted_extensions:
        print(f"{ext}: {count}")


if __name__ == "__main__":
    main()
