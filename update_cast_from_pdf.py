import json
import pdfplumber
import re

def parse_cast_list(pdf_path):
    cast_data = {"actors": [], "actor_roles": {}}
    unique_roles = set()
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            print(f"Page {page_num} raw text: {text}")  # Debug: Show raw extracted text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            i = 0
            while i < len(lines):
                line = re.sub(r'[#*]', '', lines[i].strip())  # Clean special characters first
                print(f"Processing line {i} (cleaned): {line}")  # Debug: Trace each cleaned line
                # Match colon-separated character:actor format for standalone lines
                colon_match = re.match(r'^(.+?):\s*(.+)$', line, re.IGNORECASE)
                if colon_match:
                    role, actor = colon_match.groups()
                    role = role.strip().replace('.', '').upper()
                    actor = actor.strip()
                    if actor and not re.match(r'^[A-Z][A-Za-z\s-]*$', actor):  # Skip if actor looks like a role
                        i += 1
                        continue
                    if actor and actor not in cast_data["actors"]:
                        cast_data["actors"].append(actor)
                        cast_data["actor_roles"][actor] = []
                    if role and actor in cast_data["actors"] and role not in cast_data["actor_roles"][actor]:
                        cast_data["actor_roles"][actor].append(role)
                        unique_roles.add(role)
                    print(f"Matched colon: Actor={actor}, Role={role}")
                    i += 1
                    continue
                
                # Match group header (e.g., PLANKTON POSSE)
                group_match = re.match(r'^[A-Z][A-Za-z\s-]*(?:-.*)?:$', line)
                if group_match:
                    group_role = line.rstrip(':').strip().upper()
                    i += 1
                    while i < len(lines) and not re.match(r'^[A-Z][A-Za-z\s-]*(?:-.*)?:$', lines[i]):
                        sub_line = re.sub(r'[#*]', '', lines[i].strip())  # Clean special characters
                        print(f"Processing sub-line (cleaned): {sub_line}")  # Debug: Trace sub-line
                        sub_colon_match = re.match(r'^(.+?):\s*(.+)$', sub_line, re.IGNORECASE)
                        if sub_colon_match:
                            sub_role, sub_actor = sub_colon_match.groups()
                            sub_role = sub_role.strip().replace('.', '').upper()
                            sub_actor = sub_actor.strip()
                            if sub_actor and not re.match(r'^[A-Z][A-Za-z\s-]*$', sub_actor):  # Skip if actor looks like a role
                                i += 1
                                continue
                            if sub_actor and sub_actor not in cast_data["actors"]:
                                cast_data["actors"].append(sub_actor)
                                cast_data["actor_roles"][sub_actor] = []
                            if sub_role and sub_actor in cast_data["actors"] and sub_role not in cast_data["actor_roles"][sub_actor]:
                                cast_data["actor_roles"][sub_actor].append(sub_role)
                                unique_roles.add(sub_role)
                            print(f"Matched sub-colon: Actor={sub_actor}, Role={sub_role}")
                        else:
                            sub_actor = sub_line
                            if (sub_actor and re.match(r'^[A-Za-z\s-]+$', sub_actor) and 
                                not re.match(r'^[A-Z\s-]{5,}:?$', sub_actor) and 
                                sub_actor not in unique_roles):
                                if sub_actor not in cast_data["actors"]:
                                    cast_data["actors"].append(sub_actor)
                                    cast_data["actor_roles"][sub_actor] = []
                                if group_role and sub_actor in cast_data["actors"] and group_role not in cast_data["actor_roles"][sub_actor]:
                                    cast_data["actor_roles"][sub_actor].append(group_role)
                                    unique_roles.add(group_role)
                                print(f"Matched sub-actor: {sub_actor}, Role={group_role}")
                        i += 1
                    continue
                
                # Fallback for standalone actor names, excluding header-like lines
                actor_match = re.match(r'^[A-Za-z]+(?:\s[A-Za-z]+)*$', line)
                if actor_match and not re.match(r'^[A-Z\s-]{5,}:?$', line) and line not in unique_roles and line not in cast_data["actors"]:
                    actor = line
                    if actor not in cast_data["actors"]:
                        cast_data["actors"].append(actor)
                        cast_data["actor_roles"][actor] = []
                    print(f"Matched actor: {actor}")
                
                i += 1
            
            print(f"After page {page_num}, actors: {cast_data['actors']}")
            print(f"After page {page_num}, roles: {cast_data['actor_roles']}")
    
    return cast_data, unique_roles

def save_data(cast_data, mappings_data, cast_path="cast.json", mappings_path="group_mappings.json"):
    with open(cast_path, 'w') as f:
        json.dump(cast_data, f, indent=2)
    with open(mappings_path, 'w') as f:
        json.dump(mappings_data, f, indent=2)
    print(f"Cast list updated and saved to {cast_path}. Group mappings updated and saved to {mappings_path}.")

if __name__ == "__main__":
    pdf_path = "./Cast_List/CastList.pdf"  # Assume CastList.pdf is in the same folder
    try:
        # Parse the PDF and get cast data and unique roles
        cast_data, unique_roles = parse_cast_list(pdf_path)
        
        # Create new group mappings from unique roles, mapping each to itself
        new_mappings = {role: role for role in unique_roles}
        
        # Save the new data, overwriting existing files
        save_data(cast_data, new_mappings)
    except FileNotFoundError:
        print("Error: CastList.pdf not found. Please ensure it is in the same folder as this script.")
    except Exception as e:
        print(f"Error processing the PDF: {e}")