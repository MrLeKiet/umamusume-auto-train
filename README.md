# Umamusume Auto Training Bot
 
Like the title says, this is a simple auto training for Umamusume.

This project is inspired by [samsulpanjul/umamusume-auto-train](https://github.com/samsulpanjul/umamusume-auto-train)

[Demo video](https://youtu.be/CXSYVD-iMJk)

![Screenshot](screenshot.png)

## Features

- Automatically trains Uma with stat prioritization
- Keeps racing until fan count meets the goal, and always picks races with matching aptitude
- Checks mood and handles debuffs automatically
- Rest and recreation management
- Prioritizes G1 races if available for fan farming
- Skill point check for manually skill purchasing
- Stat caps to prevent overtraining specific stats
- Improved training logic with better support card handling
- Minimum support card requirements for training (Read Logic)

## Getting Started

### Requirements

- [Python 3.10+](https://www.python.org/downloads/)

### Setup

#### Clone repository

```
git clone https://github.com/Kisegami/umamusume-auto-train/
```

#### Install dependencies

```
pip install -r requirements.txt
```

### BEFORE YOU START

Make sure these conditions are met:

- Screen resolution must be 1920x1080
- The game should be in fullscreen
- Your Uma must have already won the trophy for each race (the bot will skips the race)
- Turn off all confirmation pop-ups in game settings
- The game must be in the career lobby screen (the one with the Tazuna hint icon)

### Configuration

You can edit your configuration in `config.json`

```json
{
  "priority_stat": ["spd", "sta", "wit", "pwr", "guts"],
  "minimum_mood": "GREAT",
  "maximum_failure": 10,
  "prioritize_g1_race": true,
  "skill_point_cap": 400,
  "enable_skill_point_check": true,
  "min_support": 3,
  "stat_caps": {
    "spd": 1100,
    "sta": 1100,
    "pwr": 600,
    "guts": 600,
    "wit": 600
  }
}
```

#### Configuration Options

`priority_stat` (array of strings)
- Determines the training stat priority. The bot will focus on these stats in the given order of importance.
- Accepted values: `"spd"`, `"sta"`, `"pwr"`, `"guts"`, `"wit"`

`minimum_mood` (string)
- The lowest acceptable mood the bot will tolerate when deciding to train.
- Accepted values (case-sensitive): `"GREAT"`, `"GOOD"`, `"NORMAL"`, `"BAD"`, `"AWFUL"`
- **Example**: If set to `"NORMAL"`, the bot will train as long as the mood is `"NORMAL"` or better. If the mood drops below that, it'll go for recreation instead.

`maximum_failure` (integer)
- Sets the maximum acceptable failure chance (in percent) before skipping a training option.
- Example: 10 means the bot will avoid training with more than 10% failure risk.

`prioritize_g1_race` (boolean)
- If `true`, the bot will prioritize G1 races except during July and August (summer).
- Useful for fan farming.

`skill_point_cap` (integer) - 
- Maximum skill points before the bot prompts you to spend them.
- The bot will pause on race days and show a prompt if skill points exceed this cap.

`enable_skill_point_check` (boolean) - 
- Enables/disables the skill point cap checking feature.

`min_support` (integer) - 
- Minimum number of support cards required for training (default: 3).
- If no training meet the requirement, the bot will do race instead.
- WIT training requires at least 2 support cards regardless of this setting.
- If you want to turn this off, set it to 0

`stat_caps` (object) - 
- Maximum values for each stat. The bot will skip training stats that have reached their cap.
- Prevents overtraining and allows focusing on other stats.

Make sure the values match exactly as expected, typos might cause errors.

### Start

```
python main.py
```

To stop the bot, just press `Ctrl + C` in your terminal, or move your mouse to the top-left corner of the screen.

## Training Choice Analysis System

The bot includes a sophisticated choice analysis system that considers multiple factors when selecting training options.

### Character Profiles

Each Uma Musume character can have a specific profile that affects training decisions. Profiles are defined in `utils/character_data.py`:

```python
CHARACTER_PROFILES['character_name'] = {
    'running_style': 'leader',  # leader, runner, betweener, chaser
    'stat_bonus': {
        'spd': 1.2,  # Values above 1.0 mean better growth
        'sta': 1.0,
        'pwr': 1.1,
        'guts': 0.9,
        'wit': 1.0
    },
    'preferred_distance': 'mile',  # sprint, mile, long
    'surface_aptitude': {
        'turf': 'A',  # S, A, B, C, D ranks
        'dirt': 'B'
    }
}
```

### Training Factors

The system considers multiple factors when scoring training choices:

1. **Character-Specific Traits**:
   - Natural stat growth rates
   - Preferred running style
   - Surface aptitudes
   - Preferred race distance

2. **Running Style Requirements**:
   - Leaders: High Speed and Power focus
   - Runners: Balanced Speed and Stamina
   - Betweeners: Balanced stats with good Wisdom
   - Chasers: High Stamina and Guts for late-game

3. **Surface Aptitude Bonuses**:
   - S-rank: 30% bonus
   - A-rank: 20% bonus
   - B-rank: Standard performance
   - C-rank: 20% penalty
   - D-rank: 40% penalty

4. **Training Phase Adjustments**:
   - Early Phase: Focus on stats and bonds
   - Mid Phase: Balance stats and skills
   - Late Phase: Prioritize skills and status

5. **Stat Combinations**:
   - Speed + Power: Good for sprints
   - Stamina + Guts: Essential for long races
   - Speed + Wisdom: Good for positioning
   - Stamina + Wisdom: Important for long races

### Using the Analysis System

You can get detailed analysis of training choices:

```python
from utils.training_selector import select_best_choice

choices = [
    {
        'name': 'Speed Training',
        'effects': {'spd': 10, 'pwr': 5}
    },
    {
        'name': 'Stamina Training',
        'effects': {'sta': 12, 'guts': 6}
    }
]

# Get best choice with analysis
best = select_best_choice(
    choices=choices,
    character_id='silence_suzuka',
    race_type='mile',
    surface='turf',
    show_analysis=True
)
```

### Testing Your Configuration

You can test your character configurations using:

```bash
python tools/test_training_selection.py
```

This will show how different choices are scored for various race types and training phases.

### Adding New Characters

1. Create a new entry in `CHARACTER_PROFILES`
2. Use the `validate_character_data()` function to verify the data
3. Test the configuration with different race types
4. Check the analysis output to ensure bonuses are applied correctly

### Score Interpretation

- Higher scores indicate better training choices
- Scores are affected by:
  - Base stat gains
  - Character bonuses
  - Running style compatibility
  - Surface aptitude
  - Stat combinations
  - Training phase

The system will automatically select the highest-scoring choice that meets all requirements (minimum mood, support cards, etc.).

### Training Logic

The bot uses an improved training logic system:

1. **Junior Year**: Prioritizes training in areas with the most support cards to quickly unlock rainbow training.
2. **Senior/Classic Year**: Prioritizes rainbow training (training with support cards of the same type).
3. **Stat Caps**: Automatically skips training stats that have reached their configured caps.
4. **Support Requirements**: Ensures minimum support card requirements are met before training. If not enough support cards, do race instead.
5. **Fallback Logic**: If rainbow training isn't available, falls back to most support card logic.
6. **Rest Logic**: If energy is too low (every training have high failure rate) => Rest

#### Race Prioritization

When `prioritize_g1_race` is enabled:
- The bot will prioritize racing over training when G1 races are available
- Automatically skips July and August (summer break) for racing
- Checks skill points before race days and prompts if they exceed the cap

### Known Issues

- Some Uma that has special event/target goals (like Restricted Train Goldship or 2 G1 Race Oguri Cap) may not working. So please avoid using Goldship for training right now to keep your 12 million yen safe. For Oguri Cap, you can turn on Prioritize G1 race
- OCR might misread failure chance (e.g., reads 33% as 3%) and proceeds with training anyway.
- Sometimes it misdetects debuffs and clicks the infirmary unnecessarily (not a big deal).
- Automatically picks the top option during chain events. Be careful with Acupuncture event, it always picks the top option.
- If you bring a friend support card (like Tazuna/Aoi Kiryuin) and do recreation, the bot can't decide whether to date with the friend support card or the Uma.
- The bot will skip "3 consecutive races warning" prompt for now
- The bot stuck when "Crietia not meet" prompt appear

### TODO

- Add Race Stragety option (right now the only option is manually changing it)
- Do race that doesn't have trophy yet
- Auto-purchase skills (Partially implemented with skill point management)
- Automate Claw Machine event
- Improve OCR accuracy for failure chance detection
- Add consecutive races limit
- Add auto retry for failed races
- Add fans tracking/goal for Senior year (Valentine day, Fan Fest and Holiday Season)
- Add option to do race in Summer (July - August)
- Add better event options handling



### Contribute

If you run into any issues or something doesn't work as expected, feel free to open an issue.
Contributions are also very welcome, I would truly appreciate any support to help improve this project further.
