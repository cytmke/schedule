import csv
import json
import re

def parse_cast_list(csv_path):
    cast_data = {"actors": [], "actor_roles": {}}
    unique_roles = set()
    current_group = None
    row_count = 0

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            print(f"Reading file: {csv_path} with content preview: {f.read(100)}...")
            f.seek(0)
            reader = csv.DictReader(f)
            print(f"Detected headers: {reader.fieldnames}")
            normalized_headers = [h.strip().lower().replace('\ufeff', '') for h in reader.fieldnames]
            expected_headers = ['role', 'actor', 'group (y/n)']
            if not all(h in normalized_headers for h in expected_headers):
                raise ValueError(f"CSV is missing required headers: {expected_headers}")
            
            for row in reader:
                row_count += 1
                role = row['Role'].strip().upper() if row.get('Role') else ""
                actor = row['Actor'].strip() if row.get('Actor') else ""
                is_group = row['Group (y/n)'].strip().lower() == 'y' if row.get('Group (y/n)') else False

                if not actor:
                    print(f"Skipping row {row_count} due to missing actor: {row}")
                    continue

                # Add actor if not already present, regardless of group status
                if actor and actor not in cast_data["actors"]:
                    cast_data["actors"].append(actor)
                    cast_data["actor_roles"][actor] = []
                    print(f"Row {row_count}: Added actor {actor}")

                if is_group:
                    current_group = role
                    unique_roles.add(role)
                    print(f"Row {row_count}: Set group {current_group}")
                    if role and actor in cast_data["actors"] and role not in cast_data["actor_roles"][actor]:
                        cast_data["actor_roles"][actor].append(role)
                        unique_roles.add(role)
                        print(f"Row {row_count}: Added role {role} to {actor}")
                else:
                    if role and actor in cast_data["actors"] and role not in cast_data["actor_roles"][actor]:
                        cast_data["actor_roles"][actor].append(role)
                        unique_roles.add(role)
                        print(f"Row {row_count}: Added role {role} to {actor}")
                    if current_group and actor in cast_data["actors"] and current_group not in cast_data["actor_roles"][actor]:
                        cast_data["actor_roles"][actor].append(current_group)
                        unique_roles.add(current_group)
                        print(f"Row {row_count}: Added group role {current_group} to {actor}")

        print(f"Processed {row_count} rows, total actors: {len(cast_data['actors'])}")
        for actor in cast_data["actor_roles"]:
            cast_data["actor_roles"][actor] = list(dict.fromkeys(cast_data["actor_roles"][actor]))

        return cast_data, unique_roles
    except csv.Error as e:
        print(f"CSV parsing error at row {row_count}: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error in parse_cast_list at row {row_count}: {e}")
        raise

def save_data(cast_data, mappings_data, cast_path="cast.json", mappings_path="group_mappings.json"):
    with open(cast_path, 'w', encoding='utf-8') as f:
        json.dump(cast_data, f, indent=2, ensure_ascii=False)
    with open(mappings_path, 'w', encoding='utf-8') as f:
        json.dump(mappings_data, f, indent=2, ensure_ascii=False)
    print(f"Cast list updated and saved to {cast_path}. Group mappings updated and saved to {mappings_path}.")

if __name__ == "__main__":
    csv_path = "./Cast_List/CastList.csv"
    try:
        cast_data, unique_roles = parse_cast_list(csv_path)
        new_mappings = {role: role for role in unique_roles}
        save_data(cast_data, new_mappings)
    except FileNotFoundError:
        print("Error: CastList.csv not found. Please ensure it is in the same folder as this script.")
    except Exception as e:
        print(f"Error processing the CSV: {e}")