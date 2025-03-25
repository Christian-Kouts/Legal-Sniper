import xml.etree.ElementTree as ET
import urllib.request

def xml_to_md(xml_file_url, output_md_file):

    # Parse the XML file
    try:
        with urllib.request.urlopen(xml_file_url) as f:
            tree = ET.parse(f)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML from {xml_file_url}: {e}")
        return

    def process_element(element, output_md_file, level=0):
        indent = '\t' * level
        for child in element:
            process_element(child, output_md_file, level + 1)

    process_element(root, output_md_file)
    

if __name__ == "__main__":
    xml_to_md('https://laws-lois.justice.gc.ca/eng/XML/I-3.3.xml', 'MD Files\\I-3.3.md')
