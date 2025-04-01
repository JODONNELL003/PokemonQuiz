# Pokemon Quiz Game

A fun quiz game to test your Pokemon knowledge! Try to name as many Pokemon as you can in 60 seconds.

## Download and Play

### Windows Users
1. Go to the [Releases](https://github.com/JODONNELL003/PokemonQuiz/releases) page
2. Download the latest `PokemonQuiz.exe` from the latest release
3. Double-click the downloaded file to run the game

### How to Play
- Press SPACE to cycle through Pokemon
- Press BACKSPACE to skip Pokemon you don't know
- Try to name as many Pokemon as you can in 60 seconds
- Press ESC to quit

## Development Setup

If you want to run the game from source:

1. Clone the repository:
```bash
git clone https://github.com/JODONNELL003/PokemonQuiz.git
cd PokemonQuiz
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python pokemon_quiz.py
```

## Building the Executable

To build the Windows executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run the build command:
```bash
pyinstaller pokemon_quiz.spec
```

The executable will be created in the `dist` folder.

## Features

- Attractive windowed display (1024x768)
- Pretty animated light pink gradient background
- 60-second timer counting down
- Randomly displays Pokemon from your image collection
- Press SPACE to cycle through Pokemon
- No duplicate Pokemon until all have been shown
- End game summary with a list of all Pokemon seen
- Animated UI elements with smooth transitions
- High score system that tracks your best performance

## Setup

1. Install Python 3.7 or higher
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure your Pokemon images are in the `img` folder
   - They should be named sequentially (e.g., 001.png, 002.png, etc.)
   - The filenames will be used as Pokemon identifiers in the results screen

4. (Optional) Add sound effects to the `sounds` folder:
   - `new_pokemon.wav` - Played when showing a new Pokemon
   - `start_game.wav` - Played when starting the game
   - `end_game.wav` - Played when the game ends

## Controls

- **SPACE**: Show next Pokemon (during the game)
- **ENTER/RETURN**: Start the game (from start screen)
- **ESC**: Quit the game
- **Mouse Click**: Select buttons

## High Score System

The game automatically tracks your high scores in a `high_scores.json` file:
- Displays your all-time high score on the start screen and during gameplay
- Highlights when you achieve a new high score
- Keeps track of your 10 most recent scores with dates

## Requirements

- Python 3.7+
- Pygame 2.5.2
- Pokemon images in the `img` folder 