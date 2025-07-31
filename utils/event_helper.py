import json
import os
from typing import Dict, Tuple, Optional
from core.ocr import extract_text
from utils.screenshot import enhanced_screenshot

# Region where event text appears in the game window
EVENT_TEXT_REGION = (243, 196, 382, 72)  # Coordinates found using region selector tool

def load_config() -> Dict:
    """Load configuration including character name"""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(script_dir, "config.json")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARNING] Failed to load config: {str(e)}")
        return {}

def load_common_events() -> Dict:
    """Load common events from events.json"""
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        events_path = os.path.join(script_dir, "assets", "data", "events.json")
        with open(events_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # print(f"[DEBUG] Loaded {len(data)} events from events.json")
            # print(f"[DEBUG] Available events: {', '.join(data.keys())}")
            return data
    except Exception as e:
        print(f"[WARNING] Failed to load events.json: {str(e)}")
        return {}

def load_character_events() -> Dict:
    """Load character-specific events from characters.json"""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    char_path = os.path.join(script_dir, "assets", "data", "characters.json")
    
    try:
        with open(char_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print("[WARNING] characters.json is not a valid dictionary")
                return {}
            return data
    except Exception as e:
        print(f"[WARNING] Failed to load character events: {str(e)}")
        return {}

# Support events have been removed - all events are in characters.json

def get_event_text() -> str:
    """Capture and extract text from the event screen"""
    event_img = enhanced_screenshot(EVENT_TEXT_REGION)
    text = extract_text(event_img)
    
    # Filter out obviously wrong text
    invalid_keywords = [
        "Windows", "PowerShell", "Microsoft", "Python",
        "Administrator", "Copyright", "PS C:", "Users"
    ]
    
    # Check if the text contains any invalid keywords
    if any(keyword in text for keyword in invalid_keywords):
        print(f"\n[ERROR] Captured text appears to be from outside the game window: {text}")
        print("[ERROR] Please ensure the game window is in focus and try again")
        return ""
        
    # Clean up the text
    cleaned_text = ' '.join(text.split())  # Remove extra whitespace
    return cleaned_text

def load_support_events() -> Dict:
    """Load support card events from supports.json"""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    support_path = os.path.join(script_dir, "assets", "data", "supports.json")
    
    try:
        with open(support_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARNING] Failed to load support events: {str(e)}")
        return {}

def extract_event_info() -> Tuple[str, list]:
    """
    Extract text from event region and match with events.
    Order of checking:
    1. Character-specific events
    2. Common events
    3. Support card events
    Returns event text and choice list.
    """
    event_text = get_event_text()
    if not event_text:
        return "", []

    # Load all event data
    config = load_config()
    char_events = load_character_events()
    common_events = load_common_events()
    support_events = load_support_events()

    # Clean up and normalize the detected text
    detected_text = event_text.strip()
    detected_clean = ''.join(c.lower() for c in detected_text if c.isalnum())
    
    print(f"[DEBUG] Searching for event: '{detected_text}' (normalized: '{detected_clean}')")
    
    # 1. First check character events
    character_name = config.get("character_name")
    if character_name and character_name in char_events:
        char_data = char_events[character_name]
        # Try exact match first
        if detected_text in char_data:
            print(f"[INFO] Found character event (exact match): {detected_text}")
            return detected_text, char_data[detected_text]
        # Try normalized match
        for event_name, choices in char_data.items():
            event_clean = ''.join(c.lower() for c in event_name if c.isalnum())
            if detected_clean == event_clean:
                print(f"[INFO] Found character event (normalized match): {event_name}")
                return event_name, choices
    
    # 2. Then check common events from events.json
    # Try exact match first
    if detected_text in common_events:
        print(f"[INFO] Found common event (exact match): {detected_text}")
        return detected_text, common_events[detected_text]
    # Try normalized match
    for event_name, choices in common_events.items():
        event_clean = ''.join(c.lower() for c in event_name if c.isalnum())
        if detected_clean == event_clean:
            print(f"[INFO] Found common event (normalized match): {event_name}")
            return event_name, choices
    
    # 3. Finally check support events
    for support_name, support_data in support_events.items():
        for event_name, choices in support_data.items():
            # Try exact match first
            if detected_text == event_name:
                print(f"[INFO] Found support event (exact match) for {support_name}: {event_name}")
                return event_name, choices
            # Try normalized match
            event_clean = ''.join(c.lower() for c in event_name if c.isalnum())
            if detected_clean == event_clean:
                print(f"[INFO] Found support event (normalized match) for {support_name}: {event_name}")
                return event_name, choices
    
    print(f"[WARNING] No matching event found for text: {detected_text}")
    return detected_text, []
    
    # Try character events next
    character_name = config.get("character_name")
    if character_name and character_name in char_events:
        char_data = char_events[character_name]
        
        # Try to find matching event with exact match first
        if event_text in char_data:
            print(f"[INFO] Found character event (exact match): {event_text}")
            return event_text, char_data[event_text]
            
        # Try fuzzy matching if exact match fails
        for event_name in char_data:
            db_text = ''.join(c.lower() for c in event_name if c.isalnum())
            if detected_text == db_text or detected_text in db_text or db_text in detected_text:
                print(f"[INFO] Found character event (fuzzy match): {event_name}")
                return event_name, char_data[event_name]
    
    # If no character event match, try support events
    support_events = load_support_events()
    for support_name, support_data in support_events.items():
        for event_name, event_choices in support_data.items():
            # Try exact match first
            if event_text == event_name:
                print(f"[INFO] Found support event (exact match) for {support_name}: {event_name}")
                return event_name, event_choices
            
            # Try fuzzy match
            db_text = ''.join(c.lower() for c in event_name if c.isalnum())
            if detected_text == db_text or detected_text in db_text or db_text in detected_text:
                print(f"[INFO] Found support event (fuzzy match) for {support_name}: {event_name}")
                return event_name, event_choices
            
    print(f"[WARNING] No matching event found for text: {event_text}")
    return event_text, []
    """
    Extract text from event region and match it with character/support events.
    Returns event text and event data if found.
    """
    event_text = get_event_text()
    if not event_text:
        return "", None
        
    # Load configuration and databases
    config = load_config()
    char_events = load_character_events()
    support_events = load_support_events()
    
    character_name = config.get("character_name")
    if not character_name:
        print("[WARNING] No character_name set in config.json")
        return event_text, None
        
    # Try matching with character events first
    if character_name in char_events:
        char_event_data = char_events[character_name].get("events", {})
        for event_name, event_data in char_event_data.items():
            if event_text in event_name:
                print(f"[INFO] Matched character event: {event_name}")
                return event_text, event_data
                
    # If no character event match, try support events
    for event_name, event_data in support_events.items():
        if event_text in event_name:
            print(f"[INFO] Matched support event: {event_name}")
            return event_text, event_data
            
    print(f"[WARNING] No matching event found for text: {event_text}")
    return event_text, None

def calculate_best_choice(event_name: str, event_data: Dict, last_trained_stat: str = None) -> Tuple[int, float]:
    """
    Calculate the best choice for an event based on its data
    Returns: Tuple of (choice_number, score)
    """
    if event_name not in event_data:
        print(f"[WARNING] Unknown event: {event_name}")
        return (1, 0)  # Default to first choice for unknown events
        
    choices = event_data[event_name]["choices"]
    best_choice = 1
    best_score = float('-inf')  # Initialize to negative infinity to handle all negative scores
    
    for idx, choice in enumerate(choices, 1):
        score = 0
        
        # Handle guaranteed effects
        if "effects" in choice:
            effects = choice["effects"]
            score += effects.get("motivation", 0) * 3  # Motivation weight
            
            # Handle last trained stat penalty
            if "last_trained_stat" in effects and last_trained_stat:
                score += effects["last_trained_stat"]
                
            # Handle status effects
            if effects.get("status") == "practice_perfect":
                score += 15  # High bonus for perfect status
            elif effects.get("status") == "practice_poor":
                score -= 5  # Penalty for poor status
                
        # Handle random outcomes
        if "random_outcomes" in choice:
            outcomes = choice["random_outcomes"]
            expected_score = 0
            
            for outcome in outcomes:
                outcome_score = 0
                effects = outcome["effects"]
                
                # Calculate score for this outcome
                outcome_score += effects.get("motivation", 0) * 3
                if "last_trained_stat" in effects and last_trained_stat:
                    outcome_score += effects["last_trained_stat"]
                if effects.get("status") == "practice_perfect":
                    outcome_score += 15
                elif effects.get("status") == "practice_poor":
                    outcome_score -= 5
                    
                # Weight by probability
                expected_score += outcome_score * outcome["chance"]
                
            score = expected_score
            
        print(f"Choice {idx} score: {score}")
        
        if score > best_score:
            best_score = score
            best_choice = idx
            
    return (best_choice, best_score)

def handle_event() -> int:
    """
    Main function to handle events
    Returns: The choice number (1-3) that should be selected
    """
    event_text, event_data = extract_event_info()
    if not event_text:
        print("[WARNING] Could not read event text")
        return 1  # Default to first choice if can't read
        
    if not event_data:
        print("[WARNING] No event data found")
        return 1  # Default to first choice if no data
    
    # Try to find matching event in data
    matching_event = None
    for event_name in event_data:
        if event_name.lower() in event_text.lower():
            matching_event = event_name
            break
            
    if matching_event:
        print(f"[INFO] Found matching event: '{matching_event}'")
        
        # Get last trained stat (you'll need to implement this based on your game state tracking)
        last_trained_stat = None  # TODO: Implement this
        
        try:
            choice, score = calculate_best_choice(matching_event, event_data, last_trained_stat)
            print(f"[INFO] Event '{matching_event}' detected.")
            print(f"[INFO] Choosing option {choice} (score: {score})")
            return choice
        except Exception as e:
            print(f"[WARNING] Error calculating choice for event '{matching_event}': {str(e)}")
            return 1
    else:
        print(f"[WARNING] Unknown event: '{event_text}'")
        return 1  # Default to first choice for unknown events

def calculate_choice_score(choice: dict, last_trained_stat: str = None) -> float:
    """Helper function to calculate score for a single choice"""
    score = 0
    
    # Handle guaranteed effects
    if "effects" in choice:
        effects = choice["effects"]
        score += effects.get("motivation", 0) * 3
        if "last_trained_stat" in effects and last_trained_stat:
            score += effects["last_trained_stat"]
        if effects.get("status") == "practice_perfect":
            score += 15
        elif effects.get("status") == "practice_poor":
            score -= 5
            
    # Handle random outcomes
    if "random_outcomes" in choice:
        outcomes = choice["random_outcomes"]
        expected_score = 0
        
        for outcome in outcomes:
            outcome_score = 0
            effects = outcome["effects"]
            
            outcome_score += effects.get("motivation", 0) * 3
            if "last_trained_stat" in effects and last_trained_stat:
                outcome_score += effects["last_trained_stat"]
            if effects.get("status") == "practice_perfect":
                outcome_score += 15
            elif effects.get("status") == "practice_poor":
                outcome_score -= 5
                
            expected_score += outcome_score * outcome["chance"]
            
        score = expected_score
        
    return score
