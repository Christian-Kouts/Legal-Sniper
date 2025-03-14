import xml.etree.ElementTree as ET

def get_full_text(element):
    """Extracts all text within an element, including text from subelements."""
    return ''.join(element.itertext()).strip()

def process_heading(heading):
    """Converts an XML Heading element to a Markdown heading."""
    level = int(heading.get('level'))
    title_text = get_full_text(heading.find('TitleText'))
    label = heading.find('Label')
    if label is not None:
        title_text = f"{label.text} {title_text}"
    return f"{'#' * level} {title_text}\n\n"

def process_section(section):
    """Converts an XML Section element to Markdown, including subsections, paragraphs, etc."""
    label = section.find('Label').text
    marginal_note = get_full_text(section.find('MarginalNote')) if section.find('MarginalNote') is not None else ''
    markdown = f"**{label}. {marginal_note}**\n\n"

    # Direct text in section
    text = section.find('Text')
    if text is not None:
        markdown += f"{get_full_text(text)}\n\n"

    # Subsections
    subsections = section.findall('Subsection')
    if subsections:
        for sub in subsections:
            sub_label = sub.find('Label').text
            sub_text = get_full_text(sub.find('Text')) if sub.find('Text') is not None else ''
            sub_num = sub_label#.strip('()')
            markdown += f"\t{sub_num} {sub_text}\n"

            # Paragraphs within subsection
            paragraphs = sub.findall('Paragraph')
            if paragraphs:
                for par in paragraphs:
                    par_label = par.find('Label').text
                    par_text = get_full_text(par.find('Text'))
                    markdown += f"\t\t{par_label} {par_text}\n"

            # Continued subsection text
            continued = sub.find('ContinuedSectionSubsection')
            if continued is not None:
                cont_text = get_full_text(continued)
                markdown += f"\t{cont_text}\n"
            markdown += "\n"

    # Definitions
    definitions = section.findall('Definition')
    if definitions:
        for defn in definitions:
            text_element = defn.find('Text')
            if text_element is not None:
                term_en = text_element.find('DefinedTermEn')
                if term_en is not None:
                    term = term_en.text
                    definition = term_en.tail or ''
                    term_fr = text_element.find('DefinedTermFr')
                    if term_fr is not None:
                        fr_term = term_fr.text
                        markdown += f"**{term}**: {definition} ({fr_term})\n"
                    else:
                        markdown += f"**{term}**: {definition}\n"

            # Paragraphs within definition
            def_paragraphs = defn.findall('Paragraph')
            if def_paragraphs:
                for par in def_paragraphs:
                    par_label = par.find('Label').text
                    par_text = get_full_text(par.find('Text'))
                    markdown += f"\t{par_label} {par_text}\n"
        markdown += "\n"

    # Historical notes
    historical_note = section.find('HistoricalNote')
    if historical_note is not None:
        markdown += "*Historical Note:*\n"
        for note in historical_note.findall('HistoricalNoteSubItem'):
            markdown += f"- {get_full_text(note)}\n"
        markdown += "\n"

    return markdown

def process_body(body):
    """Processes the Body element, handling headings and sections."""
    markdown = ""
    for element in body:
        if element.tag == 'Heading':
            markdown += process_heading(element)
        elif element.tag == 'Section':
            markdown += process_section(element)
    return markdown

def xml_to_markdown(xml_file, output_file='output.md'):
    """Parses an XML file into a Markdown file, focusing on Identification and Body."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Identification section
    identification = root.find('Identification')
    long_title = get_full_text(identification.find('LongTitle'))
    short_title = get_full_text(identification.find('ShortTitle'))

    markdown = f"# {short_title}\n\n"
    markdown += f"**{long_title}**\n\n"

    # Body section
    body = root.find('Body')
    markdown += process_body(body)

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    return markdown

# Example usage
if __name__ == "__main__":
    xml_to_markdown('A-1.xml', 'A-1.md')