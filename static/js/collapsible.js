document.addEventListener('DOMContentLoaded', function() {
    // Find all pre elements that could be code outputs
    const preElements = document.querySelectorAll('pre');
    
    preElements.forEach(function(preElement, index) {
        const content = preElement.textContent;
        
        // Skip input cells (cells with "In [X]:" pattern)
        const isInputCell = preElement.textContent.trim().match(/^In \[\d+\]:/);
        
        // If it's an output cell (not an input cell) and has content, make it collapsible
        if (!isInputCell && content.trim().length > 0) {
            // Create wrapper div
            const wrapper = document.createElement('div');
            wrapper.className = 'collapsible-section';
            
            // Create header with appropriate title
            let headerText = 'Output';
            
            // Try to determine a better header based on content
            if (content.includes('Installing collected packages') || 
                content.includes('Requirement already satisfied') || 
                content.includes('Downloading')) {
                headerText = 'Package Installation Output';
            } else if (content.includes('Column Headers:')) {
                headerText = 'Data Structure Analysis';
            } else if (content.includes('DataFrame') || content.includes('Series')) {
                headerText = 'DataFrame Output';
            } else if (content.includes('Figure(')) {
                headerText = 'Plot Output';
            }
            
            const header = document.createElement('div');
            header.className = 'collapsible-header';
            header.innerHTML = `<span class="toggle-icon">►</span> <span class="header-text">${headerText}</span> <span class="preview-text">(click to expand)</span>`;
            
            // Create content container
            const contentDiv = document.createElement('div');
            contentDiv.className = 'collapsible-content collapsed'; // Start collapsed by default
            
            // Move the pre element into the content container
            preElement.parentNode.insertBefore(wrapper, preElement);
            contentDiv.appendChild(preElement);
            
            // Assemble the structure
            wrapper.appendChild(header);
            wrapper.appendChild(contentDiv);
            
            // Add click event to toggle
            header.addEventListener('click', function() {
                const isExpanded = !contentDiv.classList.contains('collapsed');
                
                if (isExpanded) {
                    contentDiv.classList.add('collapsed');
                    header.querySelector('.toggle-icon').textContent = '►';
                    header.querySelector('.preview-text').textContent = '(click to expand)';
                } else {
                    contentDiv.classList.remove('collapsed');
                    header.querySelector('.toggle-icon').textContent = '▼';
                    header.querySelector('.preview-text').textContent = '(click to collapse)';
                }
            });
        }
    });
}); 