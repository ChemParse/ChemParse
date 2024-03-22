//TOC
document.addEventListener('DOMContentLoaded', function () {
    const toc = document.querySelector('.toc');

    // Create and add the TOC title
    const tocTitle = document.createElement('h2');
    tocTitle.textContent = 'TOC';
    toc.appendChild(tocTitle);

    let blockId = 0; // Initialize a block ID counter

    document.querySelectorAll('div[data-p-type="block"]').forEach(function (element) {
        const readableName = element.getAttribute('readable-name');
        const startLine = element.getAttribute('start-line');
        const dataAvailable = element.getAttribute('data_available');
        const pSubtype = element.getAttribute('data-p-subtype');

        if (readableName && readableName !== 'Unknown') {
            element.id = 'block-' + blockId;

            const tocEntry = document.createElement('div');
            tocEntry.classList.add('toc-entry');
            tocEntry.dataset.targetId = element.id;

            // Create the color block for the TOC entry
            const colorBlock = document.createElement('div');
            colorBlock.classList.add('color-block');

            // Set the color of the block based on the same conditions as the main content
            const styles = getComputedStyle(document.documentElement);
            const availableColor = styles.getPropertyValue('--comment-available-color').trim();
            const unavailableColor = styles.getPropertyValue('--comment-unavailable-color').trim();
            const errorColor = styles.getPropertyValue('--comment-error-color').trim();

            if (pSubtype === 'unrecognized-format') {
                colorBlock.style.backgroundColor = errorColor;
            } else {
                if (dataAvailable === "1") {
                    colorBlock.style.backgroundColor = availableColor;
                } else {
                    colorBlock.style.backgroundColor = unavailableColor;
                }
            }

            // Style the color block (you can adjust these styles as needed)
            colorBlock.style.width = '10px';
            colorBlock.style.height = '10px';
            colorBlock.style.marginRight = '5px';
            colorBlock.style.display = 'inline-block';
            colorBlock.style.verticalAlign = 'middle';

            const entryText = startLine ? `Line ${startLine}: ${readableName}` : readableName;
            const textNode = document.createTextNode(entryText);

            // Append the color block and text to the TOC entry
            tocEntry.appendChild(colorBlock);
            tocEntry.appendChild(textNode);

            toc.appendChild(tocEntry);

            blockId++;
        }
    });

    document.querySelectorAll('.toc-entry').forEach(function (entry) {
        entry.addEventListener('click', function () {
            const targetId = this.dataset.targetId;
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});


// comment sidebar
document.addEventListener('DOMContentLoaded', function () {

    const mainContentArea = document.querySelector('.content');
    const sidebarCommentBlocks = [];

    const computedStyles = getComputedStyle(document.documentElement);

    const dataBlocks = document.querySelectorAll('div[data-p-type="block"]');
    dataBlocks.forEach(function (dataBlock, index) {
        const isDataAvailable = dataBlock.getAttribute('data_available');
        const blockType = dataBlock.getAttribute('data-p-subtype');
        const startLineOfBlock = dataBlock.getAttribute('start-line');
        const endLineOfBlock = dataBlock.getAttribute('finish-line');

        const commentBlockContainer = document.createElement('div');
        commentBlockContainer.classList.add('comment-section');

        const indicatorColorBlock = document.createElement('div');
        indicatorColorBlock.classList.add('indicatorColorBlock');

        // Text container that will hold both top and bottom text elements
        const textContainer = document.createElement('div');
        textContainer.classList.add('text-container');

        // Top text element for the start line number
        const topText = document.createElement('div');
        topText.textContent = startLineOfBlock;
        topText.classList.add('top-text');

        // Bottom text element for the end line number
        const bottomText = document.createElement('div');
        bottomText.textContent = endLineOfBlock;
        bottomText.classList.add('bottom-text');

        // Append top and bottom text to the text container
        textContainer.appendChild(topText);
        textContainer.appendChild(bottomText);


        const colorForAvailable = computedStyles.getPropertyValue('--comment-available-color').trim();
        const colorForUnavailable = computedStyles.getPropertyValue('--comment-unavailable-color').trim();
        const colorForError = computedStyles.getPropertyValue('--comment-error-color').trim();

        if (blockType === 'unrecognized-format') {
            indicatorColorBlock.style.backgroundColor = colorForError;
            commentBlockContainer.title = "Block looks incorrectly formatted";
        } else {
            if (isDataAvailable === "1") {
                indicatorColorBlock.style.backgroundColor = colorForAvailable;
                commentBlockContainer.title = "Data available"; // Tooltip text
            } else {
                indicatorColorBlock.style.backgroundColor = colorForUnavailable;
                commentBlockContainer.title = "Raw data available"; // Tooltip text
            }
        }

        // Append the indicator color block and text container to the comment block container
        commentBlockContainer.appendChild(indicatorColorBlock);
        commentBlockContainer.appendChild(textContainer);

        commentBlockContainer.style.height = `${dataBlock.offsetHeight}px`;
        commentBlockContainer.style.top = `${dataBlock.offsetTop}px`;

        document.querySelector('.comment-sidebar').appendChild(commentBlockContainer);
        sidebarCommentBlocks[index] = { element: commentBlockContainer, initialTop: dataBlock.offsetTop };
    });

    mainContentArea.addEventListener('scroll', function () {
        const scrolledTopPosition = this.scrollTop;
        sidebarCommentBlocks.forEach(function (sidebarBlock) {
            sidebarBlock.element.style.top = `${sidebarBlock.initialTop - scrolledTopPosition}px`;
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.querySelector('.comment-sidebar');
    let maxWidth = 30; // Start with a minimum width in case there are no text blocks or they are very small

    const commentSections = sidebar.querySelectorAll('.comment-section');
    commentSections.forEach(function (section) {
        const textBlock = section.querySelector('.text-block');
        if (textBlock) {
            // Ensure the element is visible to get accurate measurements
            textBlock.style.visibility = 'hidden';
            textBlock.style.display = 'block';

            const width = textBlock.offsetWidth + 10; // Add some padding

            // Revert visibility and display styles
            textBlock.style.visibility = '';
            textBlock.style.display = '';

            if (width > maxWidth) {
                maxWidth = width;
            }
        }
    });

    // Apply the calculated width to the sidebar
    sidebar.style.width = `${maxWidth}px`;
});
