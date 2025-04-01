# Pokemon Quiz Game

A fun and interactive Pokemon quiz game built with Pygame. Test your Pokemon knowledge by naming as many Pokemon as you can in 60 seconds!

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

## How to Play

1. Run the game:
   ```bash
   python pokemon_quiz.py
   ```
2. Click the START button or press Enter to begin the quiz
3. You have 60 seconds to identify as many Pokemon as possible
4. Press SPACE to cycle to the next Pokemon
5. When time runs out, the game will show you a list of all Pokemon you saw
6. Your score will be saved if it's a new high score
7. Click PLAY AGAIN to start a new game
8. Press ESC at any time to quit

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