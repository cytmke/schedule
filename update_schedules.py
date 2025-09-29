import json
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class ConflictResolver:
    def __init__(self, cast_data, group_mappings):
        self.cast_data = cast_data
        self.group_mappings = group_mappings
        self.resolution_cache = {}
        
    def get_all_actors(self):
        return sorted(self.cast_data.get('actors', []))
    
    def get_all_roles(self):
        roles = set()
        for actor_roles in self.cast_data.get('actor_roles', {}).values():
            for role in actor_roles:
                if role.upper() not in self.group_mappings:
                    roles.add(role)
        return sorted(roles)
    
    def get_all_groups(self):
        return sorted(self.group_mappings.keys())
    
    def is_valid_name(self, name):
        name_upper = name.upper()
        
        if name_upper == "FULL CAST":
            return True
        
        if name_upper in self.group_mappings:
            return True
        
        for actor_roles in self.cast_data.get('actor_roles', {}).values():
            if name_upper in [r.upper() for r in actor_roles]:
                return True
        
        return False
    
    def resolve_conflict(self, conflicting_name, current_date=None, current_time=None):
        if conflicting_name.upper() in self.resolution_cache:
            cached = self.resolution_cache[conflicting_name.upper()]
            if cached['type'] == 'ignore':
                return None
            elif cached['type'] == 'full_cast':
                return 'FULL CAST'
            else:
                return cached['value']
        
        result = {'action': None, 'selection': None, 'apply_all': False}
        
        root = tk.Tk()
        root.title(f"Resolve Conflict: {conflicting_name}")
        root.geometry("800x600")
        
        context_text = f"'{conflicting_name}' does not match any current role or group"
        if current_date:
            context_text += f"\n\nDate: {current_date}"
            if current_time:
                context_text += f" | Time: {current_time}"
        
        header = tk.Label(root, text=context_text, font=('Arial', 12, 'bold'), fg='red', pady=10)
        header.pack()
        
        main_frame = tk.Frame(root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        actors_frame = tk.Frame(main_frame)
        actors_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        actors_label = tk.Label(actors_frame, text="Actors (select one or more):", font=('Arial', 10, 'bold'))
        actors_label.pack(pady=5)
        
        actors_listbox = tk.Listbox(actors_frame, selectmode='multiple', height=25)
        actors_scrollbar = ttk.Scrollbar(actors_frame, orient='vertical', command=actors_listbox.yview)
        actors_listbox.config(yscrollcommand=actors_scrollbar.set)
        
        for actor in self.get_all_actors():
            actors_listbox.insert(tk.END, actor)
        
        actors_listbox.pack(side='left', fill='both', expand=True)
        actors_scrollbar.pack(side='right', fill='y')
        
        roles_frame = tk.Frame(main_frame)
        roles_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        roles_label = tk.Label(roles_frame, text="Roles (select one):", font=('Arial', 10, 'bold'))
        roles_label.pack(pady=5)
        
        roles_listbox = tk.Listbox(roles_frame, selectmode='single', height=25)
        roles_scrollbar = ttk.Scrollbar(roles_frame, orient='vertical', command=roles_listbox.yview)
        roles_listbox.config(yscrollcommand=roles_scrollbar.set)
        
        for role in self.get_all_roles():
            roles_listbox.insert(tk.END, role)
        
        roles_listbox.pack(side='left', fill='both', expand=True)
        roles_scrollbar.pack(side='right', fill='y')
        
        groups_frame = tk.Frame(main_frame)
        groups_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        groups_label = tk.Label(groups_frame, text="Groups (select one):", font=('Arial', 10, 'bold'))
        groups_label.pack(pady=5)
        
        groups_listbox = tk.Listbox(groups_frame, selectmode='single', height=25)
        groups_scrollbar = ttk.Scrollbar(groups_frame, orient='vertical', command=groups_listbox.yview)
        groups_listbox.config(yscrollcommand=groups_scrollbar.set)
        
        for group in self.get_all_groups():
            groups_listbox.insert(tk.END, group)
        
        groups_listbox.pack(side='left', fill='both', expand=True)
        groups_scrollbar.pack(side='right', fill='y')
        
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        def on_select():
            selected_actors = [actors_listbox.get(i) for i in actors_listbox.curselection()]
            selected_roles = [roles_listbox.get(i) for i in roles_listbox.curselection()]
            selected_groups = [groups_listbox.get(i) for i in groups_listbox.curselection()]
            
            total_selected = len(selected_actors) + len(selected_roles) + len(selected_groups)
            
            if total_selected == 0:
                messagebox.showerror("Error", "Please select at least one item")
                return
            
            if len(selected_roles) > 0 and len(selected_actors) > 0:
                messagebox.showerror("Error", "Cannot select both roles and actors")
                return
            
            if len(selected_groups) > 0 and (len(selected_actors) > 0 or len(selected_roles) > 0):
                messagebox.showerror("Error", "Cannot select groups with actors or roles")
                return
            
            if len(selected_roles) > 1:
                messagebox.showerror("Error", "Can only select one role")
                return
            
            if len(selected_groups) > 1:
                messagebox.showerror("Error", "Can only select one group")
                return
            
            if len(selected_roles) == 1:
                confirm = messagebox.askyesno("Confirm", f"Map '{conflicting_name}' to role '{selected_roles[0]}'?")
                if confirm:
                    result['action'] = 'role'
                    result['selection'] = selected_roles[0]
                    apply_all = messagebox.askyesno("Apply to All", f"Use '{selected_roles[0]}' for all future references to '{conflicting_name}'?")
                    result['apply_all'] = apply_all
                    root.destroy()
            
            elif len(selected_groups) == 1:
                confirm = messagebox.askyesno("Confirm", f"Map '{conflicting_name}' to group '{selected_groups[0]}'?")
                if confirm:
                    result['action'] = 'group'
                    result['selection'] = selected_groups[0]
                    apply_all = messagebox.askyesno("Apply to All", f"Use '{selected_groups[0]}' for all future references to '{conflicting_name}'?")
                    result['apply_all'] = apply_all
                    root.destroy()
            
            elif len(selected_actors) == 1:
                confirm = messagebox.askyesno("Confirm", f"Add role '{conflicting_name.upper()}' to actor '{selected_actors[0]}'?")
                if confirm:
                    result['action'] = 'new_role'
                    result['selection'] = selected_actors[0]
                    apply_all = messagebox.askyesno("Apply to All", f"Use this mapping for all future references to '{conflicting_name}'?")
                    result['apply_all'] = apply_all
                    root.destroy()
            
            elif len(selected_actors) > 1:
                actor_list = ", ".join(selected_actors)
                confirm = messagebox.askyesno("Confirm", f"Create new group '{conflicting_name.upper()}' with actors:\n{actor_list}?")
                if confirm:
                    result['action'] = 'new_group'
                    result['selection'] = selected_actors
                    apply_all = messagebox.askyesno("Apply to All", f"Use this group for all future references to '{conflicting_name}'?")
                    result['apply_all'] = apply_all
                    root.destroy()
        
        def on_ignore():
            confirm = messagebox.askyesno("Confirm", f"Ignore '{conflicting_name}'? It will not be added to the schedule.")
            if confirm:
                result['action'] = 'ignore'
                apply_all = messagebox.askyesno("Apply to All", f"Ignore all future references to '{conflicting_name}'?")
                result['apply_all'] = apply_all
                root.destroy()
        
        def on_full_cast():
            confirm = messagebox.askyesno("Confirm", f"Replace '{conflicting_name}' with 'FULL CAST'?")
            if confirm:
                result['action'] = 'full_cast'
                apply_all = messagebox.askyesno("Apply to All", f"Use 'FULL CAST' for all future references to '{conflicting_name}'?")
                result['apply_all'] = apply_all
                root.destroy()
        
        select_btn = tk.Button(button_frame, text="Select", command=on_select, width=15, bg='green', fg='white', font=('Arial', 10, 'bold'))
        select_btn.pack(side='left', padx=5)
        
        ignore_btn = tk.Button(button_frame, text="Ignore", command=on_ignore, width=15, bg='orange', fg='white', font=('Arial', 10, 'bold'))
        ignore_btn.pack(side='left', padx=5)
        
        full_cast_btn = tk.Button(button_frame, text="FULL CAST", command=on_full_cast, width=15, bg='blue', fg='white', font=('Arial', 10, 'bold'))
        full_cast_btn.pack(side='left', padx=5)
        
        root.mainloop()
        
        if result['action'] is None:
            return None
        
        if result['action'] == 'ignore':
            if result['apply_all']:
                self.resolution_cache[conflicting_name.upper()] = {'type': 'ignore'}
            return None
        
        if result['action'] == 'full_cast':
            if result['apply_all']:
                self.resolution_cache[conflicting_name.upper()] = {'type': 'full_cast'}
            return 'FULL CAST'
        
        if result['action'] == 'role' or result['action'] == 'group':
            if result['apply_all']:
                self.resolution_cache[conflicting_name.upper()] = {'type': 'mapping', 'value': result['selection']}
            return result['selection']
        
        if result['action'] == 'new_role':
            role_upper = conflicting_name.upper()
            actor = result['selection']
            if actor in self.cast_data['actor_roles']:
                if role_upper not in self.cast_data['actor_roles'][actor]:
                    self.cast_data['actor_roles'][actor].append(role_upper)
            else:
                self.cast_data['actor_roles'][actor] = [role_upper]
            
            if result['apply_all']:
                self.resolution_cache[conflicting_name.upper()] = {'type': 'mapping', 'value': role_upper}
            return role_upper
        
        if result['action'] == 'new_group':
            group_upper = conflicting_name.upper()
            self.group_mappings[group_upper] = group_upper
            
            for actor in result['selection']:
                if actor in self.cast_data['actor_roles']:
                    if group_upper not in self.cast_data['actor_roles'][actor]:
                        self.cast_data['actor_roles'][actor].append(group_upper)
                else:
                    self.cast_data['actor_roles'][actor] = [group_upper]
            
            if result['apply_all']:
                self.resolution_cache[conflicting_name.upper()] = {'type': 'mapping', 'value': group_upper}
            return group_upper
        
        return None


def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def parse_schedule(file_path, conflict_resolver):
    schedule = {}
    current_date = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for date line
            date_pattern = r'^(?:Friday|Saturday),?\s+([A-Za-z]+)\s+(\d{1,2})(?:,?\s+(\d{4}))?:?$'
            date_match = re.match(date_pattern, line, re.IGNORECASE)
            
            if date_match:
                month_name = date_match.group(1)
                day = int(date_match.group(2))
                year = int(date_match.group(3)) if date_match.group(3) else 2025
                month_num = datetime.strptime(month_name, '%B').month
                current_date = datetime(year, month_num, day).strftime('%Y-%m-%d')
                schedule[current_date] = []
                print(f"Parsed date: {line} -> {current_date}")
                i += 1
                continue
            
            if not current_date or not line:
                i += 1
                continue
            
            # Check if line is ONLY a time (no groups on same line)
            time_only_pattern = r'^\s*(\d{1,2}:\d{2}(?:am|pm)?-\d{1,2}:\d{2}(?:am|pm)?)\s*$'
            time_only_match = re.match(time_only_pattern, line)
            
            if time_only_match:
                time_range = time_only_match.group(1).strip()
                groups = []
                i += 1
                
                # Collect groups from subsequent lines
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line:
                        i += 1
                        continue
                    
                    # Check if next line is a new time or date
                    time_check_pattern = r'^\s*(\d{1,2}:\d{2}(?:am|pm)?-\d{1,2}:\d{2}(?:am|pm)?)'
                    date_check_pattern = r'^\s*(?:Friday|Saturday)'
                    if re.match(time_check_pattern, next_line) or re.match(date_check_pattern, next_line, re.IGNORECASE):
                        break
                    
                    next_groups_raw = [g.strip() for g in re.split(r',\s*', next_line) if g.strip()]
                    for group_name in next_groups_raw:
                        resolved = resolve_name(group_name, conflict_resolver, current_date, time_range)
                        if resolved:
                            groups.append(resolved.upper())
                    i += 1
                
                if groups and current_date in schedule:
                    schedule[current_date].append({"time": time_range, "groups": groups})
                    print(f"Added schedule: {current_date}, {time_range}, {groups}")
                continue
            
            # Check for time with groups on the same line
            time_groups_pattern = r'^\s*(\d{1,2}:\d{2}(?:am|pm)?-\d{1,2}:\d{2}(?:am|pm)?)\s+(.+)$'
            time_match = re.match(time_groups_pattern, line)
            
            if time_match:
                time_range = time_match.group(1).strip()
                groups_text = time_match.group(2).strip()
                
                groups_raw = [g.strip() for g in re.split(r',\s*', groups_text) if g.strip()]
                groups = []
                
                for group_name in groups_raw:
                    resolved = resolve_name(group_name, conflict_resolver, current_date, time_range)
                    if resolved:
                        groups.append(resolved.upper())
                
                # Only add to schedule if we have valid groups
                if current_date in schedule and groups:
                    schedule[current_date].append({"time": time_range, "groups": groups})
                    print(f"Added schedule: {current_date}, {time_range}, {groups}")
                
                i += 1
                
                # Only check for continuation lines if we added a schedule entry
                if groups and current_date in schedule and schedule[current_date]:
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if not next_line:
                            i += 1
                            continue
                        
                        # Check if next line is a new time or date
                        time_check_pattern = r'^\s*(\d{1,2}:\d{2}(?:am|pm)?-\d{1,2}:\d{2}(?:am|pm)?)'
                        date_check_pattern = r'^\s*(?:Friday|Saturday)'
                        if re.match(time_check_pattern, next_line) or re.match(date_check_pattern, next_line, re.IGNORECASE):
                            break
                        
                        next_groups_raw = [g.strip() for g in re.split(r',\s*', next_line) if g.strip()]
                        next_groups = []
                        
                        for group_name in next_groups_raw:
                            resolved = resolve_name(group_name, conflict_resolver, current_date, time_range)
                            if resolved:
                                next_groups.append(resolved.upper())
                        
                        if next_groups:
                            schedule[current_date][-1]["groups"].extend(next_groups)
                            print(f"Added groups to: {current_date}, {schedule[current_date][-1]['time']}, {schedule[current_date][-1]['groups']}")
                        i += 1
                continue
            
            # Handle standalone Full Cast lines for cases with no time specified
            full_cast_check = r'^\s*Full Cast\s*(?:\(optional\))?\s*$'
            if re.match(full_cast_check, line, re.IGNORECASE) and current_date in schedule:
                if not schedule[current_date]:
                    # No time slots yet for this date use default time
                    day_of_week = datetime.strptime(current_date, '%Y-%m-%d').strftime('%A')
                    default_time = "5:30pm-9:00pm" if day_of_week == "Friday" else "9:30am-2:00pm"
                    schedule[current_date].append({"time": default_time, "groups": ["FULL CAST"]})
                    print(f"Added default FULL CAST schedule: {current_date}, {default_time}, ['FULL CAST']")
                else:
                    # There are existing time slots add to the last one
                    schedule[current_date][-1]["groups"].append("FULL CAST")
                    print(f"Added FULL CAST to: {current_date}, {schedule[current_date][-1]['time']}, {schedule[current_date][-1]['groups']}")
                i += 1
            else:
                i += 1
    
    return schedule


def resolve_name(name, conflict_resolver, current_date=None, current_time=None):
    if not name or name.upper() == "WORSHIP":
        return None
    
    if conflict_resolver.is_valid_name(name):
        return name
    
    print(f"Conflict detected: '{name}' on {current_date} at {current_time}")
    resolved = conflict_resolver.resolve_conflict(name, current_date, current_time)
    return resolved


def save_schedule(schedule, schedule_path="schedules.json"):
    with open(schedule_path, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, indent=2)
    print(f"Schedule saved to {schedule_path}.")


if __name__ == "__main__":
    try:
        cast_data = load_json("cast.json")
        group_mappings = load_json("group_mappings.json")
        
        if not cast_data or not group_mappings:
            print("Error: cast.json or group_mappings.json not found.")
            exit(1)
        
        resolver = ConflictResolver(cast_data, group_mappings)
        schedule = parse_schedule("./Call_Schedule/CallSchedule.txt", resolver)
        
        save_json(cast_data, "cast.json")
        save_json(group_mappings, "group_mappings.json")
        save_schedule(schedule)
        
        print("\nProcessing complete!")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        exit(1)
    except Exception as e:
        print(f"Error processing the schedule: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
