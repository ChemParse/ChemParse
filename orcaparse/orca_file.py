import re
import uuid
import warnings

import pandas as pd

from .orca_elements import OrcaBlock, OrcaElement
from .orca_regex_settings import RegexSettings


class OrcaFile:
    # Load default settings for all instances
    default_regex_settings = RegexSettings()
    # Unpleasant way to collect all available classes
    available_types = {cls.__name__: cls for cls in (lambda f: (lambda x: x(x))(lambda y: f(
        lambda *args: y(y)(*args))))(lambda f: lambda cls: [cls] + [sub for c in cls.__subclasses__() for sub in f(c)])(OrcaElement)}

    def __init__(self, file_path: str, regex_settings: RegexSettings | None = None):
        self.file_path: str = file_path
        self.regex_settings: RegexSettings = (
            regex_settings
            if regex_settings is not None
            else OrcaFile.default_regex_settings
        )
        self.initialized = False
        with open(self.file_path, "r") as file:
            self.original_text: str = file.read()

        self._blocks: dict[str, OrcaElement] = {}
        self._marked_text: str = self.original_text

    def get_blocks(self):
        if not self.initialized:
            self.process_patterns()
        return self._blocks

    def get_marked_text(self):
        if not self.initialized:
            self.process_patterns()
        return self._marked_text

    def process_patterns(self):
        self._blocks = {}
        self._marked_text = self.original_text
        self.initialized = True

        def replace_with_marker(match):

            def find_substring_positions(text, substring):
                # method to search for the block position in the original text
                positions = [(m.start(), m.end())
                             for m in re.finditer(re.escape(substring), text)]
                return positions
            # The entire matched text
            full_match = match.group(0)

            # The specific part you want to replace (previously match.group(1))
            extracted_text = match.group(1)

            if '<@%' in extracted_text or '%@>' in extracted_text:
                warnings.warn(
                    f'Attempt to replace the marker in {p_type, p_subtype}:{extracted_text}')
                return full_match

            # Generate a unique identifier
            unique_id = str(uuid.uuid4())

            if p_type == 'Block':

                # Find all positions of the extracted text in the original text
                positions = find_substring_positions(
                    self.original_text, extracted_text)

                if not positions:
                    warnings.warn(
                        f"No match found for the extracted text: '{extracted_text}' in the original text.")
                    position, start_index, end_index = None, None, None

                elif len(positions) > 1:
                    warnings.warn(
                        f"Multiple matches found for the extracted text: '{extracted_text}' in the original text. Using the first match.")
                    start_index, end_index = positions[0]
                else:
                    start_index, end_index = positions[0]

                if start_index is not None and end_index is not None:
                    start_line = self.original_text.count(
                        '\n', 0, start_index) + 1
                    end_line = self.original_text.count('\n', 0, end_index) + 1
                    # Tuple containing start and end lines
                    position = (start_line, end_line)

            # Dynamically instantiate the class based on p_subtype or fall back to OrcaDefaultBlock
            class_name = p_subtype  # Directly use p_subtype as class name
            if class_name in self.available_types:
                if p_type == "Block":
                    # Create an instance of the class, block have position parameter
                    element_instance = self.available_types[class_name](
                        extracted_text, position=position)
                else:
                    # Create an instance of the class, block have position parameter
                    element_instance = self.available_types[class_name](
                        extracted_text)

            else:
                if p_type == "Block":
                    # Fall back to OrcaDefaultBlock and raise a warning
                    warnings.warn(
                        f"Subtype '{p_subtype}' not recognized. Falling back to OrcaBlock."
                    )
                    element_instance = OrcaBlock(
                        extracted_text, position=position)
                else:
                    # Handle other types or raise a generic warning
                    warnings.warn(
                        f"Subtype '{p_subtype}' not recognized and type '{p_type}' does not have a default."
                    )
                    element_instance = None

            if element_instance:
                # Store the instance or raw text with the unique ID
                self._blocks[unique_id] = element_instance

                # Replace the extracted text within the full match with the marker
                text_with_markers = full_match.replace(
                    extracted_text, f"<@%{p_type}|{p_subtype}|{unique_id}%@>"
                )

            else:
                text_with_markers = full_match

            return text_with_markers

        for regex in self.regex_settings.regexes:
            pattern = regex["pattern"]
            p_type = regex["p_type"]
            p_subtype = regex["p_subtype"]
            flag_names = regex["flags"]
            flags = 0
            for flag_name in flag_names:
                flags |= getattr(re, flag_name)
            compiled_pattern = re.compile(pattern, flags)
            self._marked_text = compiled_pattern.sub(
                replace_with_marker, self._marked_text)

    def get_data(self):
        def extract_data_errors_to_none(orca_element: OrcaElement):
            try:
                return orca_element.data()
            except Exception as e:
                warnings.warn(
                    f"An unexpected error occurred while extracting data from {orca_element}: {e}, returning None instead of data.\n Raw context of the element is {orca_element.raw_data}")
                return None

        return {id: extract_data_errors_to_none(block) for id, block in self._blocks.items()}

    def get_data_by_type(self, element_type: type[OrcaBlock]):
        def extract_data_errors_to_none(orca_element: OrcaElement):
            try:
                return orca_element.data()
            except Exception as e:
                warnings.warn(
                    f"An unexpected error occurred while extracting data from {orca_element}: {e}, returning None instead of data.\n Raw context of the element is {orca_element.raw_data}")
                return None

        return {id: extract_data_errors_to_none(block) for id, block in self._blocks.items() if isinstance(block, element_type)}

    # Simple CSS for styling
    default_css_content = """
:root {
    /* Color palette */
    --body-bg-color: #ffffff; /* White background for the body */
    --block-hover-bg-color: #f9f9f9; /* Light grey for block hover */
    --header-bg-color: #e8e8e8; /* Slightly darker grey for headers */
    --block-default-color: #444444; /* Dark grey for default block text */
    --block-icon-color: #4e7cb8; /* Blue for icon blocks */
    --block-unrecognized-color: #dd0063; /* Pink/red for unrecognized blocks */
    --sidebar-bg-color: #f0f0f0; /* Light grey for sidebars */
    --toc-hover-bg-color: #e0e0e0; /* Light grey for TOC entry hover */
    --comment-available-color: #00cc66; /* Green for data available */
    --comment-unavailable-color: #ffcc00; /* Yellow for raw data available */
    --comment-error-color: #ff0000; /* Red for unrecognized format */
}

body {
    font-family: Arial, sans-serif;
    display: flex;
    height: 100vh; /* Full viewport height */
    margin: 0; /* Remove default margin */
    overflow: hidden; /* Prevent scrolling on the body */
    background-color: var(--body-bg-color);
}


/* Container holding sidebars and content */
.container {
    display: flex;
    flex-direction: row;
    width: 100%;
    height: 100%;
}


/* Main content area */
.content {
    flex-grow: 1; /* Take up remaining space */
    padding: 20px 2px 20px 2px;
    /* Allow vertical scrolling and enable horizontal scrolling if needed */
    overflow-y: auto;
    overflow-x: auto;
    height: 100vh; /* Full viewport height */
    /* Ensure the content's width expands as needed to fit its contents */
    min-width: 0;
}


/* Styling for block elements */

div[data-p-type^="spacer"] {
    font-size: 1px;
}


/* Styling for block elements */

div[data-p-type^="block"] {
    display: block;
    margin: 2px 0; /* Maintain vertical spacing between blocks */
    padding: 0; /* Remove padding to allow header to align with block top */
    background-color: transparent; /* No background color by default */
    border: none;
    transition: background-color 0.3s; /* Smooth transition for hover effect */
    /* Prevent the block from having its own horizontal scrollbar */
    overflow-x: hidden;
}

/* On hover, only change the background color inside the padding area */
div[data-p-type^="block"]:hover {
    background-color: var(--block-hover-bg-color); /* Change background color on hover */
}

/* Styling for headers within blocks */
div[data-p-type^="block"] h1,
div[data-p-type^="block"] h2,
div[data-p-type^="block"] h3,
div[data-p-type^="block"] h4,
div[data-p-type^="block"] h5,
div[data-p-type^="block"] h6 {
    font-family: Arial, sans-serif;
    font-size: 16px;
    font-weight: normal;
    margin: 0; /* Remove all margins to align header with block top */
    padding: 0px; /* Add padding for the header content */
    background-color: var(--header-bg-color); /* Different background color for headers */
    border: none;
    width: calc(100% - 20px); /* Adjust width to account for padding */
}

/* Optional: Add styling for preformatted text if you use <pre> within blocks */
div[data-p-type^="block"] pre {
    border: none;
    padding: 10px;
    margin: 0;
    overflow-x: hidden;
}

/* Default block styling */
.block-default.block-default {
    color: var(--block-default-color); /* Darker text for better readability */
}

/* Specific styling for different block subtypes */
.block-icon.block-icon {
    color: var(--block-icon-color);
}

.block-unrecognized.block-unrecognized {
    color: var(--block-unrecognized-color);
}


/* Left sidebar */
.sidebar {
    flex: 0 0 300px; /* Fixed width */
    background-color: var(--sidebar-bg-color); /* Light grey background */
    padding: 20px;
    overflow-y: auto; /* Enable vertical scrolling */
}

/* TOC specific styling */
.toc {
    list-style-type: none; /* Remove default list styling */
    padding: 0; /* Remove default padding */
}

.toc h2 {
    font-size: 20px; /* Set the size for the TOC title */
    margin-bottom: 10px; /* Add some space below the TOC title */
}

.toc-entry {
    cursor: pointer; /* Change cursor to pointer to indicate clickable items */
    padding: 5px 5px; /* Add some padding for better readability */
    border: none; /* Optional: Add rounded corners for aesthetic purposes */
    margin-bottom: 5px; /* Space between TOC entries */
    transition: background-color 0.3s; /* Smooth transition for hover effect */
}

.toc-entry:hover {
    background-color: var(--toc-hover-bg-color); /* Light background color on hover for better interaction feedback */
}
/* Left comment-sidebar for color-comment sections */
.comment-sidebar {
    flex: 0 0 10px; /* Narrow width for color-comment indicators */
    background-color: var(--sidebar-bg-color); /* Matching background color */
    position: relative; /* Positioning context for color-comment sections */
    height: 100vh; /* Match the height of the main content area */
}

.color-comment {
    position: absolute; /* Absolute positioning within comment-sidebar */
    width: 100%; /* Full width of the comment-sidebar */
    /* Background color will be set dynamically by JavaScript, no default color here */
    /* The height and top properties will be set dynamically by JavaScript */
}


"""

    # Simple JavaScript for interaction
    default_js_content = """
document.addEventListener('DOMContentLoaded', function() {
    const toc = document.querySelector('.toc');
    let blockId = 0; // Initialize a block ID counter

    document.querySelectorAll('div[data-p-type="block"]').forEach(function(element) {
        const readableName = element.getAttribute('readable-name');
        const startLine = element.getAttribute('start-line'); // Get the start-line attribute value
        if (readableName && readableName !== 'Unknown') {
            // Assign a unique ID to the block element
            element.id = 'block-' + blockId;

            // Create a TOC entry for this block
            const tocEntry = document.createElement('div');
            tocEntry.classList.add('toc-entry');
            tocEntry.dataset.targetId = element.id; // Store the block's ID in the TOC entry
            
            // Include the start-line number in front of the readable name
            const entryText = startLine ? `Line ${startLine}: ${readableName}` : readableName;
            tocEntry.textContent = entryText;

            // Add the TOC entry to the TOC container
            toc.appendChild(tocEntry);

            blockId++; // Increment the block ID counter for the next block
        }
    });

    // Add click event listeners to TOC entries
    document.querySelectorAll('.toc-entry').forEach(function(entry) {
        entry.addEventListener('click', function() {
            const targetId = this.dataset.targetId; // Get the ID of the target block
            const targetElement = document.getElementById(targetId); // Find the target block by ID
            if (targetElement) {
                // Scroll to the target block in the main content area
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // TOC functionality remains unchanged

    const contentArea = document.querySelector('.content');
    const commentSections = [];

    const styles = getComputedStyle(document.documentElement); // Fetch computed styles for the root element

    // Create color-comment sections based on data availability and subtype
    const contentBlocks = document.querySelectorAll('div[data-p-type="block"]');
    contentBlocks.forEach(function(block, index) {
        const dataAvailable = block.getAttribute('data_available');
        const pSubtype = block.getAttribute('data-p-subtype'); // Get the p_subtype attribute value
        const commentSection = document.createElement('div');
        commentSection.classList.add('color-comment');

        // Fetch color values from CSS variables
        const availableColor = styles.getPropertyValue('--comment-available-color').trim(); // Green
        const unavailableColor = styles.getPropertyValue('--comment-unavailable-color').trim(); // Yellow
        const errorColor = styles.getPropertyValue('--comment-error-color').trim(); // Red

        // Set the color and title based on data availability and p_subtype
        if (pSubtype === 'unrecognized-format') {
            commentSection.style.backgroundColor = errorColor; // Red for unrecognized format
            commentSection.title = "Block looks incorrectly formatted"; // Tooltip text
        } else {
            if (dataAvailable === "1") {
                commentSection.style.backgroundColor = availableColor; // Green for data available
                commentSection.title = "Data available"; // Tooltip text
            } else {
                commentSection.style.backgroundColor = unavailableColor; // Yellow for raw data available
                commentSection.title = "Raw data available"; // Tooltip text
            }
        }

        commentSection.style.height = `${block.offsetHeight}px`;
        commentSection.style.top = `${block.offsetTop}px`;
        document.querySelector('.comment-sidebar').appendChild(commentSection);
        commentSections[index] = { element: commentSection, initialTop: block.offsetTop };
    });

    // Adjust the position of color-comment sections on scroll
    contentArea.addEventListener('scroll', function() {
        const scrollTop = this.scrollTop;
        commentSections.forEach(function(section) {
            section.element.style.top = `${section.initialTop - scrollTop}px`;
        });
    });
});

"""

    def create_html(self, css_content: str | None = None, js_content: str | None = None) -> str:
        css_content = css_content or self.default_css_content
        js_content = js_content or self.default_js_content
        # Process the text to ensure all elements are captured
        processed_text = self.get_marked_text()

        # Function to replace markers with corresponding HTML
        def replace_marker_with_html(match):
            # Extract pattern type, subtype, and unique ID from the marker
            p_type, p_subtype, unique_id = match.groups()
            # Retrieve the corresponding OrcaElement
            element = self._blocks.get(unique_id)

            if element:
                # Convert the OrcaElement to HTML
                return element.to_html()
            else:
                raise f'Failed to find the element {unique_id}'
                # If no element is found, keep the original marker
                return match.group(0)

        # Use a regex to find and replace all markers in the processed text
        marker_regex = re.compile(r'<@%([^|]+)\|([^|]+)\|([^%]+)%@>')
        body_content = marker_regex.sub(
            replace_marker_with_html, processed_text)

        # Full HTML Document Structure with CSS and JS
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        {css_content}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <!-- Left sidebar content (TOC) -->
            <div class="toc">
                <h2>TOC</h2>
                <!-- JavaScript will populate this area -->
            </div>
        </div>
        <div class="comment-sidebar">
            <!-- comment sidebar for color-comment sections -->
            <!-- JavaScript will populate this area -->
        </div>
        <div class="content">
            {body_content}
        </div>
    </div>
    <script>
        {js_content}
    </script>
</body>
</html>"""

        return html_content

    def save_as_html(self, output_file_path: str):
        # Create the HTML content
        html_content = self.create_html()

        # Write the HTML content to the specified file
        with open(output_file_path, 'w') as output_file:
            output_file.write(html_content)
