import json
import re
from datetime import datetime

def parse_schedule(file_path):
    schedule = {}
    current_date = None
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Try multiple date formats
            date_match = re.match(r'^(?:Friday|Saturday),\s*(?:September)?\s+(\d{1,2})(?:,\s+(\d{4}))?$', line, re.IGNORECASE)
            if date_match:
                day = int(date_match.group(1))
                year = date_match.group(2) if date_match.group(2) else datetime.now().year
                current_date = datetime(2025, 9, day).strftime('%Y-%m-%d')
                schedule[current_date] = []
                print(f"Parsed date: {line} -> {current_date}")
                continue
            elif re.match(r'^(?:Friday|Saturday)\s+September\s+(\d{1,2})(?::)?$', line, re.IGNORECASE):
                day = int(re.search(r'\d{1,2}', line).group())
                current_date = datetime(2025, 9, day).strftime('%Y-%m-%d')
                schedule[current_date] = []
                print(f"Parsed date: {line} -> {current_date}")
                continue
            if not current_date or not line:
                continue
            time_match = re.match(r'^(\d{1,2}:\d{2}-\d{1,2}:\d{2})\s+(.+)$', line)
            if time_match:
                time_range, groups = time_match.groups()
                groups = [g.strip().upper() for g in re.split(r',\s*', groups) if g.strip()]
                if current_date in schedule:
                    schedule[current_date].append({"time": time_range, "groups": groups})
                    print(f"Added schedule: {current_date}, {time_range}, {groups}")
            elif re.match(r'^\s*Full Cast\s*(?:\(optional\))?$', line, re.IGNORECASE) and current_date in schedule:
                # If no prior entry, add a default full-day schedule; otherwise, append to last entry
                if not schedule[current_date]:
                    schedule[current_date].append({"time": "9:30-2:00", "groups": ["FULL CAST"]})
                    print(f"Added default FULL CAST schedule: {current_date}, 9:30-2:00, ['FULL CAST']")
                else:
                    schedule[current_date][-1]["groups"].append("FULL CAST")
                    print(f"Added FULL CAST to: {current_date}, {schedule[current_date][-1]['time']}, {schedule[current_date][-1]['groups']}")
    return schedule

def save_schedule(schedule, schedule_path="schedules.json"):
    with open(schedule_path, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, indent=2)
    print(f"Schedule saved to {schedule_path}.")

if __name__ == "__main__":
    try:
        schedule = parse_schedule("./Call_Schedule/CallSchedule.txt")
        save_schedule(schedule)
    except FileNotFoundError:
        print("Error: CallSchedule.txt not found. Please ensure it is in the Call_Schedule subfolder.")
        exit(1)
    except Exception as e:
        print(f"Error processing the schedule: {e}")
        exit(1)