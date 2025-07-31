import sys
from pathlib import Path
from typing import List, Dict
import logging

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from utils.choice_analyzer import calculate_choice_score, analyze_choice

logger = logging.getLogger(__name__)

def select_best_choice(choices: List[Dict], character_id: str = None, 
                      training_phase: str = 'mid', race_type: str = 'mile',
                      surface: str = 'turf', show_analysis: bool = False) -> Dict:
    """
    Select the best choice from a list of training options
    
    Args:
        choices: List of choices with their effects
        character_id: The character being trained
        training_phase: Current training phase
        race_type: Target race type
        surface: Race surface
        show_analysis: Whether to show detailed analysis
        
    Returns:
        The best choice
    """
    best_score = -1
    best_choice = None
    
    for i, choice in enumerate(choices):
        score = calculate_choice_score(
            effects=choice['effects'],
            character_id=character_id,
            training_phase=training_phase,
            race_type=race_type,
            surface=surface
        )
        
        if score > best_score:
            best_score = score
            best_choice = choice
    
    if show_analysis and best_choice:
        # Only show detailed analysis for the winning choice
        analysis = analyze_choice(
            effects=best_choice['effects'],
            character_id=character_id,
            training_phase=training_phase,
            race_type=race_type,
            surface=surface
        )
        print("\nBest Choice Analysis:")
        print(f"Choice: {best_choice.get('name', 'Unknown')}")
        print("\nBase Effects:")
        for effect, value in analysis['base_effects'].items():
            print(f"  {effect.upper()}: {value}")
            
        print("\nCharacter Bonuses:")
        for stat, bonus in analysis['character_bonus'].items():
            print(f"  {stat.upper()}: x{bonus:.2f}")
            
        print("\nRunning Style Bonuses:")
        for stat, bonus in analysis['style_bonus'].items():
            print(f"  {stat.upper()}: x{bonus:.2f}")
            
        print(f"\nSurface Bonus: x{analysis['surface_bonus']:.2f}")
        
        if analysis['combo_bonus']:
            print("\nCombo Bonuses:")
            for combo in analysis['combo_bonus']:
                print(f"  {combo}")
                
        print(f"\nFinal Score: {analysis['final_score']:.2f}")
        
    return best_choice

# Example usage
if __name__ == "__main__":
    # Example training choices
    training_choices = [
        {
            'name': 'Speed Training',
            'effects': {
                'spd': 10,
                'pwr': 5,
                'skill_points': 1
            }
        },
        {
            'name': 'Stamina Training',
            'effects': {
                'sta': 12,
                'guts': 6,
                'skill_points': 1
            }
        },
        {
            'name': 'Power Training',
            'effects': {
                'pwr': 12,
                'spd': 4,
                'skill_points': 1
            }
        }
    ]
    
    # Normal usage - just gets the best choice
    best = select_best_choice(
        choices=training_choices,
        character_id='silence_suzuka',
        race_type='mile',
        surface='turf'
    )
    print(f"\nSelected training: {best['name']}")
    
    # With analysis - shows detailed breakdown
    print("\nAnalyzing choices for different race types:")
    for race_type in ['sprint', 'mile', 'long']:
        print(f"\n{race_type.upper()} RACE ANALYSIS")
        best = select_best_choice(
            choices=training_choices,
            character_id='silence_suzuka',
            race_type=race_type,
            surface='turf',
            show_analysis=True  # This will show the detailed breakdown
        )
