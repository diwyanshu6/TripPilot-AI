import re

def search_trains(source: str, destination: str, limit: int = 5):
    """
    Search trains between source and destination.
    Uses mock railway schedules since standard public train APIs require IRCTC partner keys.
    """
    src = (source or "Delhi").strip().lower()
    dest = (destination or "Goa").strip().lower()
    
    # Generate realistic train schedules based on common destinations in India
    trains_db = [
        {
            "train_number": "12780",
            "train_name": "Goa Express",
            "from_station": "H Nizamuddin (NZM)",
            "to_station": "Madgaon (MAO)",
            "departure": "15:15",
            "arrival": "18:30 (next day)",
            "duration": "27h 15m",
            "runs_on": "Daily",
            "classes": ["1A", "2A", "3A", "SL"],
            "fares": {"1A": 5200, "2A": 3100, "3A": 2150, "SL": 850}
        },
        {
            "train_number": "22414",
            "train_name": "NZM MAO Rajdhani",
            "from_station": "H Nizamuddin (NZM)",
            "to_station": "Madgaon (MAO)",
            "departure": "06:10",
            "arrival": "07:15 (next day)",
            "duration": "25h 05m",
            "runs_on": "Fri, Sat",
            "classes": ["1A", "2A", "3A"],
            "fares": {"1A": 6100, "2A": 4200, "3A": 3200}
        },
        {
            "train_number": "12618",
            "train_name": "Mangala LD Express",
            "from_station": "H Nizamuddin (NZM)",
            "to_station": "Madgaon (MAO)",
            "departure": "05:40",
            "arrival": "10:15 (next day)",
            "duration": "28h 35m",
            "runs_on": "Daily",
            "classes": ["2A", "3A", "SL"],
            "fares": {"2A": 2950, "3A": 2050, "SL": 790}
        }
    ]
    
    # Generic train names in case cities are different
    generic_trains = [
        {
            "train_number": "12952",
            "train_name": f"{source.upper()} - {destination.upper()} SF Express",
            "from_station": f"{source.upper()} Central",
            "to_station": f"{destination.upper()} Junction",
            "departure": "17:00",
            "arrival": "08:30 (next day)",
            "duration": "15h 30m",
            "runs_on": "Daily",
            "classes": ["1A", "2A", "3A", "SL"],
            "fares": {"1A": 4500, "2A": 2800, "3A": 1900, "SL": 650}
        },
        {
            "train_number": "12954",
            "train_name": f"{source.upper()} - {destination.upper()} Duronto",
            "from_station": f"{source.upper()} Terminus",
            "to_station": f"{destination.upper()} Central",
            "departure": "23:15",
            "arrival": "13:45 (next day)",
            "duration": "14h 30m",
            "runs_on": "Mon, Wed, Sat",
            "classes": ["1A", "2A", "3A"],
            "fares": {"1A": 5100, "2A": 3200, "3A": 2200}
        }
    ]

    # If user wants Delhi to Goa/Madgaon, return specific db
    if ("delhi" in src or "nzm" in src or "ndls" in src) and ("goa" in dest or "mao" in dest or "madgaon" in dest):
        return trains_db[:limit]
    
    # Else customize generic schedules
    return generic_trains[:limit]
