import xml.etree.ElementTree as ET
import pandas as pd

# Parse the XML content (assuming the XML is in a string or file)
# For this example, replace 'path_to_xml_file.xml' with the actual file path
# If you have the XML as a string, use: tree = ET.fromstring(xml_string)
tree = ET.parse('A-1.xml')
root = tree.getroot()

# Find the Body element where sections are located
body = root.find('Body')

# Find all Section elements within the Body
sections = body.findall('Section')

# Initialize a list to store the table data
data = []

# Process each section
for section in sections:
    section_label = section.find('Label').text
    # Skip the definitions section (Section 3)
    if section_label == '3':
        continue
    
    # Check if the section has subsections
    subsections = section.findall('Subsection')
    if subsections:
        # Process each subsection
        for subsection in subsections:
            # Get subsection label, default to 'n/a' if not present
            subsection_label_elem = subsection.find('Label')
            subsection_label = subsection_label_elem.text if subsection_label_elem is not None else 'n/a'
            
            # Initialize content string
            content = ''
            
            # Include MarginalNote if present
            marginal_note = subsection.find('MarginalNote')
            if marginal_note is not None:
                content += ''.join(marginal_note.itertext()) + ': '
            
            # Include Text if present
            text = subsection.find('Text')
            if text is not None:
                content += ''.join(text.itertext()) + ' '
            
            # Include Paragraphs if present
            paragraphs = subsection.findall('Paragraph')
            for paragraph in paragraphs:
                content += ''.join(paragraph.itertext()) + ' '
            
            # Include ContinuedSectionSubsection if present
            css = subsection.find('ContinuedSectionSubsection')
            if css is not None:
                content += ''.join(css.itertext()) + ' '
            
            # Clean the content: remove extra whitespace
            content = ' '.join(content.split()).strip()
            
            # Add to data list
            data.append({
                'section': section_label,
                'subsection': subsection_label,
                'content': content
            })
    else:
        # No subsections, treat as a single entry with 'n/a' subsection
        subsection_label = 'n/a'
        content = ''
        
        # Include MarginalNote if present
        marginal_note = section.find('MarginalNote')
        if marginal_note is not None:
            content += ''.join(marginal_note.itertext()) + ': '
        
        # Include Text if present
        text = section.find('Text')
        if text is not None:
            content += ''.join(text.itertext()) + ' '
        
        # Clean the content: remove extra whitespace
        content = ' '.join(content.split()).strip()
        
        # Add to data list
        data.append({
            'section': section_label,
            'subsection': subsection_label,
            'content': content
        })

# Create a pandas DataFrame from the data
df = pd.DataFrame(data)

# Display the table (optional, for verification)
print(df)

# Save to CSV for further use (e.g., embedding)
df.to_csv('act_sections.csv', index=False)