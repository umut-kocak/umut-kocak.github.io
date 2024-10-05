import os
import re

def process_navigation_content(content, filename):
    """
    Process the navigation content to add a class 'selected' to the <li> item
    that matches the given filename.
    """
    # Create a regex pattern to match the <li> item where href matches the filename
    pattern = re.compile(r'(<li(?:\sclass="[^"]*")?>\s*<a\s+href="{}">.*?</a>)'.format(re.escape(filename)), re.IGNORECASE)
    
    # Replace the matching <li> item with a modified version that includes 'class="selected"'
    modified_content = pattern.sub(lambda match: match.group(0).replace('<li>', '<li class="selected">'), content)
    
    return modified_content


def process_prefixes(content, path_prefix_to_root):
    """
    Processes the HTML content to prepend path_prefix_to_root to:
    1. All local href links that end with .html.
    2. All script src attributes that include paths starting with js/.
    3. All image or other src attributes that include paths starting with assets/.

    Args:
    - content: The HTML file content as a string.
    - path_prefix_to_root: The prefix to be prepended to all relevant paths.

    Returns:
    - The updated HTML content with modified href, script src, and image src attributes.
    """

    # Pattern to match href="XXX.html"
    href_pattern = r'href="([^"]+\.html)"'

    # Pattern to match <script src="js/XXX"></script>
    script_pattern = r'src="(js/[^"]+\.js)"'

    # Pattern to match src="assets/images/XXX"
    assets_pattern = r'src="(assets/[^"]+)"'

    # Replace href links by prepending the path_prefix_to_root
    modified_content = re.sub(
        href_pattern,
        lambda match: f'href="{path_prefix_to_root}{match.group(1)}"',
        content
    )

    # Replace script src links by prepending the path_prefix_to_root before js/
    modified_content = re.sub(
        script_pattern,
        lambda match: f'src="{path_prefix_to_root}{match.group(1)}"',
        modified_content
    )

    # Replace assets src links by prepending the path_prefix_to_root before assets/
    modified_content = re.sub(
        assets_pattern,
        lambda match: f'src="{path_prefix_to_root}{match.group(1)}"',
        modified_content
    )

    return modified_content

def include_common(filepath, common_path, path_prefix_to_root):
    """
    Opens the file with the given filename, finds the <div> with an id matching
    the common file's name, and replaces only the content between the opening
    <div> and the corresponding closing </div>, keeping the surrounding tags.
    Uses a counter to handle nested divs and ensure correct matching of tags.
    """
    common_file = os.path.basename(common_path)
    print(f"Including {common_file}.")
    # Extract the base name of the common file without extension (e.g., common_XXX.html -> common_XXX)
    common_id = os.path.splitext(common_file)[0]

    # Read the contents of the target file
    with open(filepath, 'r', encoding='utf-8') as file:
        file_contents = file.readlines()  # Read the file line by line

    # Prepare the div tag to find
    opening_div_tag = f'<div id="{common_id}">'
    closing_div_tag = '</div>'

    new_contents = []
    inside_target_div = False
    div_counter = 0  # Counter to track nested divs
    replaced = False

    # To collect content before closing div
    temp_content = []

    # Read the contents of the common file
    with open(common_path, 'r', encoding='utf-8') as common:
        common_content = common.read()

        # Process the content if it is common_navigation.html
        if common_file == 'common_navigation.html':
            common_content = process_navigation_content(common_content, os.path.basename(filepath))

        common_content = process_prefixes(common_content, path_prefix_to_root)


    for line in file_contents:
        stripped_line = line.lstrip()  # Remove leading whitespace for comparison

        # If we find the opening div tag and we're not already inside the target div
        if opening_div_tag in stripped_line and not inside_target_div:
            inside_target_div = True   # Start looking for the closing div tag
            div_counter = 1  # We've found the first div, so set the counter to 1

            # Prepare to replace the content after we find the closing div
            temp_content = [common_content + '\n']
            replaced = True
            new_contents.append(line)  # Keep the line with the opening div tag
            continue  # Skip appending the current line (opening div) twice

        elif inside_target_div:
            if '<div' in stripped_line:
                div_counter += 1  # Increment for every nested div
            if closing_div_tag in stripped_line:
                div_counter -= 1  # Decrement for every closing div
                # If div_counter reaches 0, this is the correct closing tag
                if div_counter == 0:
                    inside_target_div = False  # We're done with the replacement
                    new_contents.extend(temp_content)  # Add the common file content
                    new_contents.append(line)  # Add the closing </div> tag
                    continue  # Skip appending the current line (closing div) twice
            # Skip all lines until we find the matching closing </div>
            continue

        # If we're not inside the target div, just keep the line as it is
        new_contents.append(line)

    # Write the updated content back to the original file
    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(new_contents)

    # Print a message indicating the replacement
    if not replaced:
        print(f"No matching <div> found for {common_file} in {filepath}")

def include_commons(file_path, common_paths, path_prefix_to_root):
    """
    Function that processes a file by including the common files.
    It loops through the common files and calls include_common for each file.
    """
    print(f"\nIncluding commons into {file_path}")
    for common_path in common_paths:
        include_common(file_path, common_path, path_prefix_to_root)

def should_include_commons(filename):
    """
    Predicate function to determine if the file should include common files.
    Only files that do not start with 'common_' should include common files.
    """
    return not filename.startswith('common_')

def traverse_files_non_recursive(common_files):
    """
    Traverses all files with an html suffix in the current folder,
    checks if they should include common files, and if so, processes 
    the file by including the common files.
    """
    current_folder = os.path.dirname(os.path.realpath(__file__))
    
    # List all files in the current folder (non-recursive)
    for filename in os.listdir(current_folder):
        # Check if the file has an html suffix
        if filename.endswith('.html'):
            # Use the should_include_commons function to check if the file should include commons
            if should_include_commons(filename):
                include_commons(filename, common_files)

def traverse_files(common_paths):
    """
    Recursively traverses all files with an html suffix in the current folder and its subfolders.
    Checks if they should include common files, and if so, processes the file by including the common files.
    """
    current_folder = os.path.dirname(os.path.realpath(__file__))

    # Traverse the folder recursively
    for root, dirs, files in os.walk(current_folder):
        for filename in files:
            # Check if the file has an html suffix
            if filename.endswith('.html'):
                # Use the should_include_commons function to check if the file should include commons
                if should_include_commons(filename):
                    # Full path of the file
                    file_path = os.path.join(root, filename)

                    # Calculate the depth of the subfolder
                    relative_path = os.path.relpath(root, current_folder)
                    path_prefix_to_root = './'
                    if relative_path != '.':
                        # Create the prefix to navigate back to the starting folder
                        depth = relative_path.count(os.sep) + 1
                        path_prefix_to_root += '../' * depth

                    # Process the file
                    include_commons(file_path, common_paths, path_prefix_to_root)

def find_common_html_files():
    """
    Finds all HTML files starting with 'common_' in the 'html_commons' folder and returns their full paths.
    """
    # Define the folder where we want to look for files
    commons_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'html_commons')
    
    # Check if the 'html_commons' folder exists
    if not os.path.exists(commons_folder):
        print(f"The folder {commons_folder} does not exist.")
        return []

    # List all files in the 'html_commons' folder and collect full paths
    common_paths = []
    for filename in os.listdir(commons_folder):
        # Check if the file starts with 'common_' and has an html suffix
        if filename.startswith('common_') and filename.endswith('.html'):
            # Add the full file path to the list
            full_path = os.path.join(commons_folder, filename)
            common_paths.append(full_path)
    
    return common_paths

if __name__ == "__main__":
    # First, find all 'common_' HTML files
    common_paths = find_common_html_files()

    # Then, traverse and process the other HTML files, including commons where necessary
    traverse_files(common_paths)
