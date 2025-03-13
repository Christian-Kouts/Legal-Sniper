import xml.etree.ElementTree as ET

def xml_to_md(xml_file, output_md_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

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
                level = int(child.get('level'))
                title = child.find('TitleText').text
                label = child.find('Label')
                label_text = f"{label.text} " if label is not None else ""
                md += f"{'#' + '#' * level} {label_text}{title}\n"
            elif child.tag == 'Section':
                md += handle_section(child)

    # Write to markdown file
    with open(output_md_file, 'w', encoding='utf-8') as f:
        f.write(md)

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
        definition_text = text_elem.find('DefinedTermEn').tail.strip()
        # Remove any trailing French term if present
        if '(' in definition_text:
            definition_text = definition_text.split('(')[0].strip()
        md = f"- **{defined_term}**{definition_text}\n"
    else:
        md = ""

    # Handle nested paragraphs within definition (e.g., 'business day')
    for para in definition.findall('Paragraph'):
        md += handle_paragraph(para)
    return md

def handle_paragraph(paragraph):
    para_label = paragraph.find('Label').text
    para_text = ''.join(paragraph.find('Text').itertext())
    md = f"\t- {para_label} {para_text}\n"

    #Process subparagraph content
    for subchild in paragraph:
        if subchild.tag == 'Subparagraph':
            md += handle_subparagraph(subchild)
    return md

def handle_subparagraph(subparagraph):
    subpara_label = subparagraph.find('Label').text
    subpara_text = ''.join(subparagraph.find('Text').itertext())
    md = f"\t\t- {subpara_label} {subpara_text}\n"
    return md

# Example usage
xml_to_md('A-1.xml', 'A-1 v2.md')