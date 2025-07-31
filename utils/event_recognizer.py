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

def find_event_choice_button(choice_num: int, total_choices: int = None) -> Optional[Tuple[int, int]]:
    """
    Find and return the coordinates of the specified choice button
    Args:
        choice_num: The choice number (1-3)
        total_choices: Total number of choices in the event (2 or 3)
    Returns:
        Tuple of (x, y) coordinates or None if not found
    """
    try:
        if total_choices == 2:
            if choice_num == 1:
                region = (254, 600, 84, 93)  # Region for choice 1 (2-choice events)
            else:
                region = (255, 707, 83, 100)  # Region for choice 2 (2-choice events)
        else:
            if choice_num == 1:
                region = (254, 478, 84, 93)  # Region for choice 1 (3-choice events)
            elif choice_num == 2:
                region = (255, 596, 83, 97)  # Region for choice 2 (3-choice events)
            else:
                region = (255, 706, 83, 101)  # Region for choice 3 (3-choice events)
                
        print(f"[DEBUG] Scanning region for choice {choice_num}: x={region[0]}, y={region[1]}, w={region[2]}, h={region[3]}")
        
        # Scan for the button in the exact region
        button = pyautogui.locateOnScreen(
            f"assets/buttons/choices/choice_{choice_num}.png",
            confidence=0.8,  # Slightly lower confidence for better matching
            minSearchTime=1.0,  # Longer search time
            region=region,  # Use exact region
            grayscale=True  # Use grayscale for better matching
        )
        
        if button:
            # Get the actual center of where the button was found
            x, y = pyautogui.center(button)
            print(f"[DEBUG] Choice {choice_num} button found at: ({x}, {y})")
            return (x, y)  # Return the actual detected position
        
        print(f"[DEBUG] Button {choice_num} not found in region {region}")
        return None
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

def click_choice(choice_num: int, total_choices: int = None, dry_run: bool = False) -> bool:
    """
    Click the specified choice button
    Args:
        choice_num: Which choice to click (1-3)
        total_choices: Total number of choices in the event (2 or 3)
        dry_run: If True, only scan for buttons without clicking
    Returns: True if successful, False otherwise
    """
    print(f"\n[DEBUG] Starting choice button scan...")
    
    try:
        print(f"[DEBUG] Looking for choice {choice_num} (total choices: {total_choices})...")
        
        # Define exact click coordinates for each choice
        if total_choices == 2:
            if choice_num == 1:
                region = (274, 620, 44, 53)
                click_x = 274 + 22  # center of width (44/2)
                click_y = 620 + 26  # center of height (53/2)
            else:
                region = (275, 727, 43, 60)
                click_x = 275 + 21  # center of width (43/2)
                click_y = 727 + 30  # center of height (60/2)
        else:  # 3 choices
            if choice_num == 1:
                region = (273, 498, 49, 64)
                click_x = 273 + 24  # center of width (49/2)
                click_y = 498 + 32  # center of height (64/2)
            elif choice_num == 2:
                region = (275, 616, 43, 57)
                click_x = 275 + 21  # center of width (43/2)
                click_y = 616 + 28  # center of height (57/2)
            else:
                region = (275, 726, 43, 61)
                click_x = 275 + 21  # center of width (43/2)
                click_y = 726 + 30  # center of height (61/2)
                
        # Just verify the button is there
        button = pyautogui.locateCenterOnScreen(
            f"assets/buttons/choices/choice_{choice_num}.png",
            confidence=0.8,
            minSearchTime=0.5,
            region=region
        )
        
        if button:
            print(f"[DEBUG] Choice {choice_num} found in region")
            
            if dry_run:
                print(f"[DEBUG] Dry run completed - button found")
                return True
                
            try:
                # Focus window by clicking above the choice first
                pyautogui.click(click_x, click_y - 50)
                time.sleep(0.3)
                
                # Then click the actual choice
                pyautogui.moveTo(click_x, click_y, duration=0.2)
                pyautogui.click()
                print(f"[DEBUG] Successfully clicked choice {choice_num} at position ({click_x}, {click_y})")
                print(f"[DEBUG] Click sequence: Moved to ({click_x}, {click_y-50}) first, then clicked at ({click_x}, {click_y})")
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
