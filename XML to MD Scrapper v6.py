import xml.etree.ElementTree as ET
import pandas as pd
import os
import urllib.request

def xml_to_md(xml_file, output_md_file):
    # Parse the XML file
    try:
        with urllib.request.urlopen(xml_file) as f:
            tree = ET.parse(f)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML from {xml_file}: {e}")
        return

    # Initialize markdown content
    md = ""

    # Handle Identification section
    identification = root.find('Identification')
    if identification is not None:
        long_title = identification.find('LongTitle').text
        short_title = identification.find('ShortTitle').text
        chapter = identification.find('Chapter/ConsolidatedNumber').text
        md += f"# {long_title}\n"
        md += f"**Short Title:** {short_title}\n"
        md += f"**Chapter:** {chapter}\n"

    # Handle Body section
    body = root.find('Body')
    if body is not None:
        for child in body:
            if child.tag == 'Heading':
                md += handle_heading(child)
            elif child.tag == 'Section':
                md += handle_section(child)

    # Write to markdown file
    with open(output_md_file, 'w', encoding='utf-8') as f:
        f.write(md)

def handle_heading(heading):
    level = int(heading.get('level'))
    title_text_element = heading.find('TitleText')
    title = title_text_element.text if title_text_element is not None else ""
    label = heading.find('Label')
    label_text = f"{label.text} " if label is not None else ""
    return f"{'#' + '#' * level} {label_text}{title}\n"

def handle_section(section):
    label = section.find('Label').text
    marginal_note = section.find('MarginalNote')
    marginal_note_text = ''.join(marginal_note.itertext()) if marginal_note is not None else ''
    md = f"##### {label}. {marginal_note_text}\n"

    # Process section content
    for subchild in section:
        if subchild.tag == 'Text':
            md += f"{''.join(subchild.itertext())}\n"
        elif subchild.tag == 'Subsection':
            md += handle_subsection(subchild)
        elif subchild.tag == 'Definition':
            md += handle_definition(subchild)
        elif subchild.tag == 'Paragraph':
            md += handle_paragraph(subchild)
        elif subchild.tag == 'HistoricalNote':
            continue  # Ignore historical notes
    # md += "\n"
    return md

def handle_subsection(subsection):
    label = subsection.find('Label').text
    marginal_note = subsection.find('MarginalNote')
    marginal_note_text = ''.join(marginal_note.itertext()) if marginal_note is not None else ''
    md = f"###### {label} {marginal_note_text}\n"

    # Process subsection content
    for child in subsection:
        if child.tag == 'Text':
            md += f"{''.join(child.itertext())}\n"
        elif child.tag == 'Paragraph':
            md += handle_paragraph(child)
        elif child.tag == 'ContinuedSectionSubsection':
            md += f"{''.join(child.find('Text').itertext())}\n"
        elif child.tag == 'HistoricalNote':
            continue  # Ignore historical notes
    return md

def handle_definition(definition):
    text_elem = definition.find('Text')
    if text_elem is not None:
        defined_term = text_elem.find('DefinedTermEn').text
        tail = text_elem.find('DefinedTermEn').tail
        definition_text = tail.strip() if tail else ""        
        # Remove any trailing French term if present
        if definition_text and definition_text[-1] == '(':
            definition_text = definition_text[:-1].strip()
        md = f"- **{defined_term}**{definition_text}\n"
    else:
        md = ""

    # Handle nested paragraphs within definition (e.g., 'business day')
    for para in definition.findall('Paragraph'):
        md += handle_paragraph(para)
    return md

def handle_paragraph(paragraph):
    # remove possible french term
    for fr in paragraph.find('Text').findall('DefinedTermFr'):
        fr.clear()
    
    para_text = ''.join(paragraph.find('Text').itertext())
    if para_text[-1] == '(':
        para_text = para_text[:-1].strip()

    para_label = paragraph.find('Label').text
    
    md = f"\t- {para_label} {para_text}\n"
    #Process subparagraph content
    for subchild in paragraph:
        if subchild.tag == 'Subparagraph':
            md += handle_subparagraph(subchild)
    return md

def handle_subparagraph(subparagraph):
    # Get the main label and text for the subparagraph
    label_elem = subparagraph.find('Label')
    text_elem = subparagraph.find('Text')
    subpara_label = label_elem.text if label_elem is not None else ""
    subpara_text = ''.join(text_elem.itertext()) if text_elem is not None else ""
    
    # Start the markdown with the subparagraph's label and text
    md = f"\t\t- {subpara_label} {subpara_text}\n"
    
    # Process any additional child elements (e.g., Clause, ContinuedSubparagraph) in order
    for child in subparagraph:
        if child.tag in ['Label', 'Text']:
            continue  # Already processed
        if child.tag == 'Clause':
            clause_label = child.find('Label').text if child.find('Label') is not None else ""
            clause_text = ''.join(child.find('Text').itertext()) if child.find('Text') is not None else ""
            md += f"\t\t\t- {clause_label} {clause_text}\n"
        elif child.tag == 'ContinuedSubparagraph':
            cont_text = ''.join(child.find('Text').itertext()) if child.find('Text') is not None else ""
            # Append continued text on the same line
            md += f" {cont_text}"
    return md

def main():
    # Create the output directory if it doesn't exist
    output_dir = 'C:\\Users\\chris\\Documents\\md files'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the CSV file
    try:
        df = pd.read_csv('All Acts.csv')
    except FileNotFoundError:
        print("Error: 'All Acts.csv' not found.")
        return
    except Exception as e:
        print(f"Error reading 'All Acts.csv': {e}")
        return

    # Loop through the 'xml_link' column
    for index, row in df.iterrows():
        xml_link = row['xml_link']
        
        # Extract filename from the URL
        filename = xml_link.split('/')[-1].replace('.xml', '').replace('.XML', '')
        output_md_file = os.path.join(output_dir, f'{filename}.md')

        print(f"Processing {xml_link}...")
        xml_to_md(xml_link, output_md_file)
        print(f"Generated {output_md_file}")

if __name__ == "__main__":
    # main()
    xml_to_md('https://laws-lois.justice.gc.ca/eng/XML/I-3.3.xml', 'MD Files\\I-3.3.md')