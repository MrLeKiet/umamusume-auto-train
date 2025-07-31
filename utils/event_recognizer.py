import pyautogui
import time
from typing import Optional, Tuple

def wait_for_user_confirmation():
    """Wait for user to press Y to continue or N to skip"""
    while True:
        response = input("\nPress Y to execute this choice, N to skip (default: N): ").strip().upper()
        if response == "Y":
            return True
        elif response == "" or response == "N":
            return False

def find_event_choice_button(choice_num: int) -> Optional[Tuple[int, int]]:
    """
    Find and return the coordinates of the specified choice button
    Args:
        choice_num: The choice number (1-3)
    Returns:
        Tuple of (x, y) coordinates or None if not found
    """
    try:
        # Define the region where choice buttons should appear (x, y, width, height)
        # Coordinates tuned for choice button detection
        region = (271, 398, 566, 604)  # x, y, width, height for choice button area
        
        button = pyautogui.locateCenterOnScreen(
            f"assets/buttons/choices/choice_{choice_num}.png",
            confidence=0.95,  # Higher confidence for more accurate matches
            minSearchTime=0.5,
            region=region  # Restrict search to the specified region
        )
        return button if button else None
    except Exception as e:
        print(f"[ERROR] Failed to locate choice button {choice_num}: {str(e)}")
        return None

last_event_state = False
last_event_message_time = 0
event_message_cooldown = 2  # Only print event messages every 2 seconds

def is_event_screen() -> tuple[bool, tuple[int, int] | None]:
    """
    Check if we're currently on an event screen by looking for choice 1 button
    Returns: Tuple of (is_event_screen, button_position)
    """
    global last_event_state, last_event_message_time
    current_time = time.time()
    
    try:
        # Define the region where choice buttons should appear
        region = (271, 398, 566, 604)  # x, y, width, height for choice button area
        
        # Look directly for choice 1 button as it appears in all event screens
        choice1_button = pyautogui.locateCenterOnScreen(
            "assets/buttons/choices/choice_1.png",
            confidence=0.95,  # Higher confidence for more accurate matches
            minSearchTime=0.2,
            region=region  # Restrict search to the specified region
        )
        
        current_state = bool(choice1_button)
        should_print = (current_state != last_event_state) or (current_time - last_event_message_time >= event_message_cooldown)
        
        if choice1_button and should_print:
            x, y = choice1_button
            print(f"[DEBUG] Event screen detected - Choice 1 button found at: ({x}, {y})")
            last_event_message_time = current_time
            last_event_state = True
            return True, (x, y)
        
        if should_print and not choice1_button:
            print("[DEBUG] No event screen - Choice 1 button not found")
            last_event_message_time = current_time
            
        last_event_state = current_state
        return bool(choice1_button), choice1_button if choice1_button else None
    except Exception as e:
        print(f"[ERROR] Failed to check event screen: {str(e)}")
        return False, None

def click_choice(choice_num: int, dry_run: bool = False) -> bool:
    """
    Click the specified choice button
    Args:
        choice_num: Which choice to click (1-3)
        dry_run: If True, only scan for buttons without clicking
    Returns: True if successful, False otherwise
    """
    print(f"\n[DEBUG] Starting choice button scan...")
    
    # Only look for the specific choice we want
    try:
        print(f"[DEBUG] Looking for choice {choice_num}...")
        button = pyautogui.locateCenterOnScreen(
            f"assets/buttons/choices/choice_{choice_num}.png",
            confidence=0.8,
            minSearchTime=0.5
        )
        
        if button:
            x, y = button
            print(f"[DEBUG] Choice {choice_num} found at: ({x}, {y})")
            
            if dry_run:
                print(f"[DEBUG] Dry run completed - button found")
                return True
                
            try:
                # Focus window by clicking above the choice first
                pyautogui.click(x, y - 50)
                time.sleep(0.3)
                
                # Then click the actual choice
                pyautogui.moveTo(x, y, duration=0.2)
                pyautogui.click()
                print(f"[DEBUG] Successfully clicked choice {choice_num} at position ({x}, {y})")
                print(f"[DEBUG] Click sequence: Moved to ({x}, {y-50}) first, then clicked at ({x}, {y})")
                return True
            except Exception as e:
                print(f"[ERROR] Failed to click choice {choice_num}: {str(e)}")
                return False
        else:
            print(f"[DEBUG] Choice {choice_num} not found")
            return False
            
    except Exception as e:
        print(f"[DEBUG] Error during search: {str(e)}")
        return False
