import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_character_data(character_id: str, data: dict) -> bool:
    """
    Validate character data format and values.
    
    Args:
        character_id: Character identifier
        data: Character data dictionary
        
    Returns:
        bool: True if data is valid, False otherwise
    """
    try:
        # Check required keys
        required_keys = ['running_style', 'stat_bonus', 'preferred_distance', 'surface_aptitude']
        for key in required_keys:
            if key not in data:
                logger.error(f"Missing required key '{key}' for character {character_id}")
                return False
        
        # Validate running style
        valid_styles = ['leader', 'runner', 'betweener', 'chaser']
        if data['running_style'] not in valid_styles:
            logger.error(f"Invalid running style '{data['running_style']}' for {character_id}")
            return False
        
        # Validate stat bonus
        required_stats = ['spd', 'sta', 'pwr', 'guts', 'wit']
        for stat in required_stats:
            if stat not in data['stat_bonus']:
                logger.error(f"Missing stat '{stat}' in stat_bonus for {character_id}")
                return False
            if not isinstance(data['stat_bonus'][stat], (int, float)):
                logger.error(f"Stat bonus for '{stat}' must be a number for {character_id}")
                return False
        
        # Validate preferred distance
        valid_distances = ['sprint', 'mile', 'long']
        if data['preferred_distance'] not in valid_distances:
            logger.error(f"Invalid preferred distance '{data['preferred_distance']}' for {character_id}")
            return False
        
        # Validate surface aptitude
        required_surfaces = ['turf', 'dirt']
        valid_ranks = ['S', 'A', 'B', 'C', 'D']
        for surface in required_surfaces:
            if surface not in data['surface_aptitude']:
                logger.error(f"Missing surface '{surface}' in surface_aptitude for {character_id}")
                return False
            if data['surface_aptitude'][surface] not in valid_ranks:
                logger.error(f"Invalid rank '{data['surface_aptitude'][surface]}' for {surface} in {character_id}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating character data for {character_id}: {str(e)}")
        return False

# Character base stats and growth rates
CHARACTER_PROFILES = {
    'silence_suzuka': {
        'running_style': 'leader',
        'stat_bonus': {
            'spd': 1.3,  # Strong speed growth
            'sta': 1.0,
            'pwr': 1.1,
            'guts': 0.9,
            'wit': 1.0
        },
        'preferred_distance': 'mile',
        'surface_aptitude': {
            'turf': 'A',
            'dirt': 'B'
        }
    },
    'special_week': {
        'running_style': 'betweener',
        'stat_bonus': {
            'spd': 1.1,
            'sta': 1.2,  # Good stamina growth
            'pwr': 1.1,
            'guts': 1.0,
            'wit': 0.9
        },
        'preferred_distance': 'mile',
        'surface_aptitude': {
            'turf': 'A',
            'dirt': 'B'
        }
    },
    'tokai_teio': {
        'running_style': 'leader',
        'stat_bonus': {
            'spd': 1.2,
            'sta': 1.0,
            'pwr': 1.2,  # Strong power growth
            'guts': 1.0,
            'wit': 0.9
        },
        'preferred_distance': 'mile',
        'surface_aptitude': {
            'turf': 'A',
            'dirt': 'A'  # Good on both surfaces
        }
    },
    'oguri_cap': {
        'running_style': 'runner',
        'stat_bonus': {
            'spd': 1.2,
            'sta': 1.1,
            'pwr': 1.0,
            'guts': 1.0,
            'wit': 1.0
        },
        'preferred_distance': 'mile',
        'surface_aptitude': {
            'turf': 'A',
            'dirt': 'A'
        }
    },
    'gold_ship': {
        'running_style': 'chaser',
        'stat_bonus': {
            'spd': 1.0,
            'sta': 1.2,
            'pwr': 0.9,
            'guts': 1.2,  # Strong guts growth
            'wit': 1.0
        },
        'preferred_distance': 'long',
        'surface_aptitude': {
            'turf': 'A',
            'dirt': 'C'
        }
    },
    'mejiro_mcqueen': {
        'running_style': 'leader',
        'stat_bonus': {
            'spd': 1.2,
            'sta': 1.0,
            'pwr': 1.1,
            'guts': 1.0,
            'wit': 1.0
        },
        'preferred_distance': 'mile',
        'surface_aptitude': {
            'turf': 'S',  # Excellent on turf
            'dirt': 'B'
        }
    },
    't.m._opera_o': {
        'running_style': 'chaser',
        'stat_bonus': {
            'spd': 1.0,
            'sta': 1.3,  # Excellent stamina growth
            'pwr': 1.1,
            'guts': 1.0,
            'wit': 0.9
        },
        'preferred_distance': 'long',
        'surface_aptitude': {
            'turf': 'A',
            'dirt': 'A'
        }
    }
}

# Running style specific training bonuses
RUNNING_STYLE_BONUS = {
    'leader': {
        'spd': 1.2,    # Leaders need high speed
        'sta': 0.9,    # Less focus on stamina
        'pwr': 1.1,    # Good power for starts
        'guts': 1.0,
        'wit': 1.0
    },
    'runner': {
        'spd': 1.1,
        'sta': 1.1,    # Balanced speed and stamina
        'pwr': 1.0,
        'guts': 1.0,
        'wit': 1.1     # Good wisdom for positioning
    },
    'betweener': {
        'spd': 1.1,    # Balanced stats
        'sta': 1.1,
        'pwr': 1.0,
        'guts': 1.0,
        'wit': 1.1
    },
    'chaser': {
        'spd': 0.9,    # Less initial speed
        'sta': 1.2,    # High stamina for late surge
        'pwr': 1.0,
        'guts': 1.2,   # High guts for final sprint
        'wit': 1.0
    }
}

# Surface aptitude multipliers
SURFACE_APTITUDE_BONUS = {
    'S': 1.3,  # Perfect aptitude
    'A': 1.2,  # Great aptitude
    'B': 1.0,  # Good aptitude
    'C': 0.8,  # Poor aptitude
    'D': 0.6,  # Very poor aptitude
}
