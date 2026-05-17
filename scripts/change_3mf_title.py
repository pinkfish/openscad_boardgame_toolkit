import zipfile
import tempfile
import shutil
import os
import xml.etree.ElementTree as ET
import argparse

def change_3mf_title(file_path, new_title):
    # 1. Create a temporary directory for extraction
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 2. Extract the 3MF contents
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 3. Path to the model file containing metadata
        model_path = os.path.join(temp_dir, '3D', '3dmodel.model')
        
        # 4. Parse and update the XML using regex to preserve all formatting and namespaces
        import re
        with open(model_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
            
        pattern = r'(<([a-zA-Z0-9_]+:)?object\s+[^>]*?name=[\'"])([^\'"]*)([\'"][^>]*>)'
        matches = re.findall(pattern, xml_content)
        if len(matches) == 1:
            xml_content = re.sub(pattern, r'\g<1>' + new_title + r'\g<4>', xml_content)
        elif len(matches) > 1:
            counter = [1]
            def replace_with_counter(match):
                replacement = f"{match.group(1)}{new_title} {counter[0]}{match.group(4)}"
                counter[0] += 1
                return replacement
            xml_content = re.sub(pattern, replace_with_counter, xml_content)
        else:
            print("Warning: No <object> tag with a 'name' attribute found.")
            
        with open(model_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        # 5. Re-zip the modified files
        new_3mf_path = file_path + ".tmp"
        with zipfile.ZipFile(new_3mf_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root_dir, dirs, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(full_path, temp_dir)
                    zip_out.write(full_path, rel_path)
        
        # Replace original file
        shutil.move(new_3mf_path, file_path)
        print(f"Title successfully changed to '{new_title}'")

    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Change the title metadata of a 3MF file.")
    parser.add_argument("file", help="Path to the 3MF file")
    parser.add_argument("title", help="New title for the 3MF file")
    args = parser.parse_args()
    
    change_3mf_title(args.file, args.title)