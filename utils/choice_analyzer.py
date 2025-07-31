# Effect weights based on training context
EFFECT_WEIGHTS = {
    'mood': 2.5,        # Mood affects training success
    'motivation': 2.5,  # Motivation affects training success
    'skill_points': {
        'early': 0.8,   # Focus on stats early
        'mid': 1.5,     # Balance stats and skills
        'late': 2.0     # Prioritize skills late game
    },
    'bond': {
        'early': 1.0,   # Bond is more important early for better training
        'mid': 0.7,
        'late': 0.5
    },
    'status': {
        'practice_perfect': 15,  # Very valuable
        'practice_poor': -8,     # Quite bad
        'heal_negative': 12,     # Very valuable - increased from 10
        'hot_topic': 5,         # Good status
        'overload': -7,         # Training overload - worse than tired
        'tired': -5,           # Tired status - increased penalty
        'good_mood': 3,        # Added good mood status
        'good_feeling': 4      # Added feeling good status
    },
    # Base stats modified by race type and surface
    'stats': {
        'turf': {
            'sprint': {  # 1000-1400m
                'spd': 4.0,
                'sta': 2.0,
                'pwr': 3.5,
                'guts': 2.5,
                'wit': 3.0     # Increased for turf
            },
            'mile': {   # 1600-2000m
                'spd': 3.5,
                'sta': 3.5,
                'pwr': 3.0,
                'guts': 2.5,
                'wit': 3.5     # Important for turf miles
            },
            'long': {   # 2200m+
                'spd': 2.5,
                'sta': 4.5,    # Very important for long
                'pwr': 2.5,
                'guts': 3.0,
                'wit': 3.5     # Important for turf
            }
        },
        'dirt': {
            'sprint': {  # 1000-1400m
                'spd': 4.0,
                'sta': 2.0,
                'pwr': 4.0,    # Power more important on dirt
                'guts': 3.0,   # Guts more important on dirt
                'wit': 2.0
            },
            'mile': {   # 1600-2000m
                'spd': 3.5,
                'sta': 3.0,
                'pwr': 3.5,    # Power important for dirt miles
                'guts': 3.5,   # Guts important for dirt
                'wit': 2.5
            },
            'long': {   # 2200m+
                'spd': 2.5,
                'sta': 4.0,
                'pwr': 3.0,    # Still need power for dirt
                'guts': 4.0,   # Guts very important for long dirt
                'wit': 2.5
            }
        }
    },
    # Training compatibility bonuses
    'stat_combo': {
        'spd_pwr': 1.2,    # Speed + Power good combo
        'sta_guts': 1.2,   # Stamina + Guts good combo
        'spd_wit': 1.1,    # Speed + Wisdom decent for positioning
        'sta_wit': 1.1     # Stamina + Wisdom good for long races
    },
    'heal_status': 7.0     # Increased from 5.0 - healing is important
}

from .character_data import CHARACTER_PROFILES, RUNNING_STYLE_BONUS, SURFACE_APTITUDE_BONUS

import logging
import sys
from pathlib import Path
from typing import Dict, Optional, Union

# Add the project root directory to Python path if not already there
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.character_data import CHARACTER_PROFILES, RUNNING_STYLE_BONUS, SURFACE_APTITUDE_BONUS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_choice(effects: Dict[str, Union[int, float]],
                  character_id: Optional[str] = None,
                  training_phase: str = 'mid',
                  race_type: str = 'mile',
                  surface: str = 'turf') -> Dict[str, Union[float, str, Dict]]:
    """
    Analyze a training choice and return detailed breakdown of the score.
    
    Args:
        effects: Dictionary of effects and their values
        character_id: Character ID (optional) - if not provided, uses balanced weights
        training_phase: 'early', 'mid', or 'late' phase of training
        race_type: 'sprint', 'mile', or 'long' based on target race
        surface: 'turf' or 'dirt' for race surface
        
    Returns:
        Dict containing score and breakdown of calculations
    """
    score_info = {
        'total_score': 0,
        'base_effects': {},
        'character_bonus': {},
        'style_bonus': {},
        'surface_bonus': 0,
        'combo_bonus': [],
        'final_score': 0
    }

    # Default profile if no character specified or not found
    default_profile = {
        'running_style': 'runner',
        'stat_bonus': {'spd': 1.0, 'sta': 1.0, 'pwr': 1.0, 'guts': 1.0, 'wit': 1.0},
        'preferred_distance': 'mile',
        'surface_aptitude': {'turf': 'B', 'dirt': 'B'}
    }
    
    # Get character profile
    character = CHARACTER_PROFILES.get(character_id, default_profile) if character_id else default_profile
    
    # Get running style bonuses
    style_bonus = RUNNING_STYLE_BONUS.get(character['running_style'], RUNNING_STYLE_BONUS['runner'])
    
    # Get surface aptitude bonus
    surface_aptitude = character['surface_aptitude'].get(surface, 'B')
    surface_bonus = SURFACE_APTITUDE_BONUS.get(surface_aptitude, 1.0)
    score_info['surface_bonus'] = surface_bonus
    
    stat_effects = {}
    score = 0
    
    for effect, value in effects.items():
        if effect in ['spd', 'sta', 'pwr', 'guts', 'wit']:
            try:
                # Base weight for race type and surface
                base_weight = EFFECT_WEIGHTS['stats'][surface][race_type][effect]
                
                # Character's natural stat bonus
                char_bonus = character['stat_bonus'].get(effect, 1.0)
                score_info['character_bonus'][effect] = char_bonus
                
                # Running style bonus
                style_multiplier = style_bonus.get(effect, 1.0)
                score_info['style_bonus'][effect] = style_multiplier
                
                # Store base effect
                score_info['base_effects'][effect] = value
                
                # Calculate contribution
                final_weight = base_weight * char_bonus * style_multiplier * surface_bonus
                score += value * final_weight
                
                # Store for combo calculation
                stat_effects[effect] = value
                
            except KeyError:
                score += value
                score_info['base_effects'][effect] = value
                
        elif effect == 'skill_points':
            weight = EFFECT_WEIGHTS['skill_points'][training_phase]
            score += value * weight
            score_info['base_effects']['skill_points'] = value
            
        elif effect in EFFECT_WEIGHTS:
            if isinstance(EFFECT_WEIGHTS[effect], dict):
                weight = EFFECT_WEIGHTS[effect].get(training_phase, 
                    EFFECT_WEIGHTS[effect].get('base', 1.0))
            else:
                weight = EFFECT_WEIGHTS[effect]
            score += value * weight
            score_info['base_effects'][effect] = value
    
    # Apply stat combo bonuses
    if len(stat_effects) >= 2:
        if 'spd' in stat_effects and 'pwr' in stat_effects:
            score *= EFFECT_WEIGHTS['stat_combo']['spd_pwr']
            score_info['combo_bonus'].append('Speed+Power')
            
        if 'sta' in stat_effects and 'guts' in stat_effects:
            score *= EFFECT_WEIGHTS['stat_combo']['sta_guts']
            score_info['combo_bonus'].append('Stamina+Guts')
            
        if 'spd' in stat_effects and 'wit' in stat_effects:
            score *= EFFECT_WEIGHTS['stat_combo']['spd_wit']
            score_info['combo_bonus'].append('Speed+Wisdom')
            
        if 'sta' in stat_effects and 'wit' in stat_effects:
            score *= EFFECT_WEIGHTS['stat_combo']['sta_wit']
            score_info['combo_bonus'].append('Stamina+Wisdom')
    
    score_info['final_score'] = score
    return score_info

def calculate_choice_score(effects: Dict[str, Union[int, float]], 
                         character_id: Optional[str] = None,
                         training_phase: str = 'mid', 
                         race_type: str = 'mile',
                         surface: str = 'turf') -> float:
    """
    Calculate a score for training choices based on effects and character profile.
    
    Args:
        effects: Dictionary of effects and their values
        character_id: Character ID (optional) - if not provided, uses balanced weights
        training_phase: 'early', 'mid', or 'late' phase of training
        race_type: 'sprint', 'mile', or 'long' based on target race
        surface: 'turf' or 'dirt' for race surface
        
    Returns:
        float: Score value for the choice
    """
    """
    Calculate a score for a set of effects
    
    Args:
        effects: Dictionary of effects and their values
        training_phase: 'early', 'mid', or 'late' phase of training
        race_type: 'sprint', 'mile', or 'long' based on target race
        surface: 'turf' or 'dirt' for race surface
    """
    score = 0
    stat_effects = {}  # Track stat effects for combo bonuses
    
    # Default balanced profile if no character specified or not found
    default_profile = {
        'running_style': 'runner',
        'stat_bonus': {'spd': 1.0, 'sta': 1.0, 'pwr': 1.0, 'guts': 1.0, 'wit': 1.0},
        'preferred_distance': 'mile',
        'surface_aptitude': {'turf': 'B', 'dirt': 'B'}
    }
    
    # Get character profile if specified
    if character_id:
        character = CHARACTER_PROFILES.get(character_id)
        if character:
            logger.debug(f"Using profile for {character_id}")
        else:
            logger.warning(f"Character {character_id} not found, using default profile")
            character = default_profile
    else:
        logger.debug("No character specified, using default profile")
        character = default_profile
    
    # Get running style bonuses (default to runner if invalid style)
    try:
        style_bonus = RUNNING_STYLE_BONUS[character['running_style']]
    except KeyError:
        style_bonus = RUNNING_STYLE_BONUS['runner']
    
    # Get surface aptitude bonus (default to B rank if invalid)
    try:
        surface_aptitude = character['surface_aptitude'].get(surface, 'B')
        surface_bonus = SURFACE_APTITUDE_BONUS.get(surface_aptitude, 1.0)
    except (KeyError, AttributeError):
        surface_bonus = 1.0  # Default multiplier
    
    for effect, value in effects.items():
        if effect == 'status':
            score += EFFECT_WEIGHTS['status'].get(value, 0)
            
        elif effect == 'skill_points':
            # Adjust skill points weight based on training phase
            weight = EFFECT_WEIGHTS['skill_points'][training_phase]
            score += value * weight
            
        elif effect == 'bond':
            # Adjust bond weight based on training phase
            weight = EFFECT_WEIGHTS['bond'][training_phase]
            score += value * weight
            
        elif effect in ['spd', 'sta', 'pwr', 'guts', 'wit']:
            # Store stat effect for combo calculation
            stat_effects[effect] = value
            try:
                # 1. Base weight for race type and surface
                base_weight = EFFECT_WEIGHTS['stats'][surface][race_type][effect]
                
                # 2. Character's natural stat bonus (default to 1.0 if missing)
                char_bonus = character['stat_bonus'].get(effect, 1.0)
                
                # 3. Running style bonus (default to 1.0 if missing)
                style_multiplier = style_bonus.get(effect, 1.0)
                
                # Combine all factors
                final_weight = base_weight * char_bonus * style_multiplier * surface_bonus
                score += value * final_weight
                
                # Store stat effect for combo calculation
                stat_effects[effect] = value
                
            except KeyError:
                # If any weight lookup fails, use default weight of 1.0
                score += value
                
        elif effect == 'random_stats':
            # Calculate expected value for random stats using race-appropriate weights
            weights = EFFECT_WEIGHTS['stats'][surface][race_type]
            avg_stat_weight = sum(weights.values()) / len(weights)
            total_stat_impact = value['count'] * value['value'] * avg_stat_weight
            score += total_stat_impact
            
        elif effect in ['mood', 'motivation', 'heal_status']:
            score += value * EFFECT_WEIGHTS[effect]
            
        elif effect in EFFECT_WEIGHTS:
            if isinstance(EFFECT_WEIGHTS[effect], dict):
                weight = EFFECT_WEIGHTS[effect].get(training_phase, EFFECT_WEIGHTS[effect].get('base', 1.0))
            else:
                weight = EFFECT_WEIGHTS[effect]
            score += value * weight
    
    # Apply stat combo bonuses if multiple stats are trained
    if len(stat_effects) >= 2:
        if 'spd' in stat_effects and 'pwr' in stat_effects:
            score *= EFFECT_WEIGHTS['stat_combo']['spd_pwr']
            logger.debug(f"Applied Speed+Power combo bonus")
        if 'sta' in stat_effects and 'guts' in stat_effects:
            score *= EFFECT_WEIGHTS['stat_combo']['sta_guts']
            logger.debug(f"Applied Stamina+Guts combo bonus")
        if 'spd' in stat_effects and 'wit' in stat_effects:
            score *= EFFECT_WEIGHTS['stat_combo']['spd_wit']
            logger.debug(f"Applied Speed+Wisdom combo bonus")
        if 'sta' in stat_effects and 'wit' in stat_effects:
            score *= EFFECT_WEIGHTS['stat_combo']['sta_wit']
            logger.debug(f"Applied Stamina+Wisdom combo bonus")
    
    logger.debug(f"Final score: {score}")
    return score
