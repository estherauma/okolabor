"""
Script to auto tag templates for use with Django's {% translate %} tag.
"""
import os
import re

from bs4 import BeautifulSoup, Comment

TEMPLATE_DIR = "recruiting"  # Update with the path to your templates
EXTENSIONS = [".html"]  # Add other extensions if needed

def wrap_translate_tags(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    soup = BeautifulSoup(content, "html.parser")

    # Find text nodes that aren't inside <script> or other non-translatable tags
    for text_node in soup.find_all(string=True):
        if isinstance(text_node, Comment):
            continue
        parent_tag = text_node.parent.name
        if (parent_tag not in ["script", "style"]
            and text_node.strip() and not text_node.strip().startswith("{%") # Skip template tags
            and "{{" not in text_node # Skip template tags
            and not text_node.strip().startswith("$") # Skip money
            and not re.search(r"\d+%", text_node.strip()) # Skip text with percentage
            and not re.search(r"^[\d/]+$", text_node.strip()) # Skip text that is just a number or date
            and not re.search(r"^[\d/]+$", text_node.strip()) # Skip text that is just a number or date
            and "@" not in text_node # Skip text that might be an email
            and re.search(r"[a-zA-Z]", text_node.strip()) # Must have at least one letter
            ):
            # Wrap untranslated text in {% translate %}
            wrapped_text = '{% translate "' + text_node.strip() + '" %}'
            text_node.replace_with(wrapped_text)
            print(wrapped_text)

    # Write updated content back to the file
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(soup.prettify())


def process_templates(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in EXTENSIONS):
                filepath = os.path.join(root, file)
                print(f"Processing: {filepath}")
                wrap_translate_tags(filepath)

if __name__ == "__main__":
    process_templates(TEMPLATE_DIR)
