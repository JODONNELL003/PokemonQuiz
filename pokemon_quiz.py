import pygame
import os
import random
import time
import math
import json
import csv
import sys
from typing import List, Set

# Helper function for PyInstaller asset bundling
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        print(f"Running in PyInstaller bundle. Base path: {base_path}")
    except Exception:
        # Not running in a PyInstaller bundle, use current directory
        base_path = os.path.abspath(".")
        print(f"Running in development mode. Base path: {base_path}")

    full_path = os.path.join(base_path, relative_path)
    print(f"Resource path for '{relative_path}': {full_path}")
    return full_path

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 205, 50)
BLUE = (50, 150, 255)
GRAY = (100, 100, 100)
LIGHT_PINK = (255, 220, 230)
PINK = (255, 192, 203)
DARK_PINK = (255, 150, 180)
GOLD = (255, 215, 0)
TIMER_DURATION = 60  # 60 seconds
POKEMON_NAMES_FILE = resource_path("pokemon_names.csv")

# Get a writable location for high scores
def get_highscore_path():
    """Get a writable path for high scores that persists across app launches"""
    try:
        # For Mac/Linux
        if os.name == 'posix':
            home = os.path.expanduser("~")
            app_data_dir = os.path.join(home, ".pokemonquiz")
        # For Windows
        else:
            app_data_dir = os.path.join(os.getenv('APPDATA'), "PokemonQuiz")
            
        # Create the directory if it doesn't exist
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)
            
        scores_path = os.path.join(app_data_dir, "high_scores.json")
        print(f"High scores will be saved to: {scores_path}")
        
        # Initialize with empty high scores if the file doesn't exist
        if not os.path.exists(scores_path):
            # Path to the template file
            template_path = resource_path("empty_high_scores.json")
            if os.path.exists(template_path):
                print(f"Initializing high scores with template from: {template_path}")
                try:
                    # Copy the template
                    with open(template_path, 'r') as src:
                        template_data = src.read()
                    with open(scores_path, 'w') as dest:
                        dest.write(template_data)
                    print(f"Successfully initialized high scores file.")
                except Exception as e:
                    print(f"Error initializing high scores: {e}")
            else:
                print(f"Template file not found at: {template_path}")
                print("Creating default empty high scores file")
                try:
                    with open(scores_path, 'w') as f:
                        json.dump({"top_score": 0, "recent_scores": []}, f)
                except Exception as e:
                    print(f"Error creating default high scores: {e}")
        
        return scores_path
    except Exception as e:
        print(f"Error creating high scores directory: {e}")
        # Fallback to current directory
        return resource_path("empty_high_scores.json")

HIGH_SCORE_FILE = get_highscore_path()

# Set up the display (windowed)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pokémon Who?")

# Load fonts
title_font = pygame.font.Font(None, 80)
large_font = pygame.font.Font(None, 60)
medium_font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)

class AnimatedGradient:
    def __init__(self, width, height, colors, speed=0.01):
        self.width = width
        self.height = height
        self.colors = colors
        self.speed = speed
        self.time = 0
        self.surface = pygame.Surface((width, height))
        
    def update(self):
        self.time += self.speed
        if self.time > 2 * math.pi:
            self.time = 0
            
    def draw(self, surface):
        # Create a soft oscillating gradient
        color_index = (math.sin(self.time) + 1) / 2  # Value between 0 and 1
        
        # Interpolate between the two colors
        r = int(self.colors[0][0] + (self.colors[1][0] - self.colors[0][0]) * color_index)
        g = int(self.colors[0][1] + (self.colors[1][1] - self.colors[0][1]) * color_index)
        b = int(self.colors[0][2] + (self.colors[1][2] - self.colors[0][2]) * color_index)
        
        # Fill the surface with the interpolated color
        self.surface.fill((r, g, b))
        
        # Blit the gradient surface onto the target surface
        surface.blit(self.surface, (0, 0))

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, font=medium_font, 
                 border_radius=10, border_width=2, border_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.default_color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.border_radius = border_radius
        self.border_width = border_width
        self.border_color = border_color
        
    def draw(self, surface):
        # Check if mouse is over button
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Draw button with appropriate color
        button_color = self.hover_color if is_hovered else self.color
        pygame.draw.rect(surface, button_color, self.rect, border_radius=self.border_radius)
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, self.rect, 
                         width=self.border_width, border_radius=self.border_radius)
        
        # Render text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        return is_hovered
        
    def is_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        return self.rect.collidepoint(mouse_pos) and mouse_clicked

class Checkbox:
    def __init__(self, x, y, width, height, text, checked=False, font=small_font, 
                text_color=BLACK, box_color=WHITE, check_color=GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.box_rect = pygame.Rect(x, y, height, height)  # Square box
        self.text = text
        self.checked = checked
        self.font = font
        self.text_color = text_color
        self.box_color = box_color
        self.check_color = check_color
        
    def draw(self, surface):
        # Draw the checkbox box
        pygame.draw.rect(surface, self.box_color, self.box_rect, border_radius=3)
        pygame.draw.rect(surface, BLACK, self.box_rect, width=2, border_radius=3)
        
        # Draw the checkmark if checked
        if self.checked:
            inner_rect = pygame.Rect(
                self.box_rect.x + 4, 
                self.box_rect.y + 4, 
                self.box_rect.width - 8, 
                self.box_rect.height - 8
            )
            pygame.draw.rect(surface, self.check_color, inner_rect, border_radius=2)
        
        # Render text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(midleft=(self.box_rect.right + 10, self.box_rect.centery))
        surface.blit(text_surf, text_rect)
        
    def is_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        if self.rect.collidepoint(mouse_pos) and mouse_clicked:
            return True
        return False
        
    def toggle(self):
        self.checked = not self.checked
        return self.checked

class HighScoreManager:
    def __init__(self, file_path=HIGH_SCORE_FILE):
        self.file_path = file_path
        self.high_scores = self.load_high_scores()
        
    def load_high_scores(self):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            else:
                # Initial empty high scores object
                initial_scores = {"top_score": 0, "recent_scores": []}
                
                # Try to load from template if available
                template_path = resource_path("empty_high_scores.json")
                if os.path.exists(template_path) and template_path != self.file_path:
                    try:
                        print(f"Loading high scores template from: {template_path}")
                        with open(template_path, 'r') as f:
                            initial_scores = json.load(f)
                    except Exception as e:
                        print(f"Error loading template, using default: {e}")
                
                # Save it immediately to create the file
                try:
                    # Create parent directory if it doesn't exist
                    parent_dir = os.path.dirname(self.file_path)
                    if parent_dir and not os.path.exists(parent_dir):
                        os.makedirs(parent_dir)
                        
                    with open(self.file_path, 'w') as f:
                        json.dump(initial_scores, f)
                    print(f"Created new high scores file at {self.file_path}")
                except Exception as e:
                    print(f"Failed to create high scores file: {e}")
                return initial_scores
        except Exception as e:
            print(f"Error loading high scores: {e}")
            return {"top_score": 0, "recent_scores": []}
            
    def save_high_scores(self):
        try:
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(self.file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
                print(f"Created directory: {parent_dir}")
            
            with open(self.file_path, 'w') as f:
                json.dump(self.high_scores, f)
                
            print(f"Saved high scores to {self.file_path}")
            
            # Ensure file is readable/writable by the user
            try:
                if os.name == 'posix':  # Unix/Mac
                    os.chmod(self.file_path, 0o644)
            except Exception as e:
                print(f"Warning: Could not set file permissions: {e}")
                
        except Exception as e:
            print(f"Error saving high scores: {e}")
            print(f"Attempted to save to: {self.file_path}")
            
    def add_score(self, score, date=None):
        if date is None:
            date = time.strftime("%Y-%m-%d %H:%M:%S")
            
        # Update top score if needed
        if score > self.high_scores["top_score"]:
            self.high_scores["top_score"] = score
            
        # Add to recent scores
        self.high_scores["recent_scores"].append({"score": score, "date": date})
        
        # Keep only the most recent 10 scores
        if len(self.high_scores["recent_scores"]) > 10:
            self.high_scores["recent_scores"] = self.high_scores["recent_scores"][-10:]
            
        # Save to file
        self.save_high_scores()
        
    def get_top_score(self):
        return self.high_scores["top_score"]
        
    def get_recent_scores(self):
        return self.high_scores["recent_scores"]

def load_pokemon_names():
    """Load Pokemon names from CSV file"""
    pokemon_dict = {}
    
    print(f"Attempting to load Pokemon names from: {POKEMON_NAMES_FILE}")
    
    # Try to load from CSV file
    if os.path.exists(POKEMON_NAMES_FILE):
        try:
            with open(POKEMON_NAMES_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        # Keep the original ID with leading zeros
                        pokemon_id = row[0]
                        pokemon_name = row[1].strip()
                        pokemon_dict[pokemon_id] = pokemon_name
                        
            print(f"Loaded {len(pokemon_dict)} Pokemon names from CSV")
            # Print first 5 entries as sample
            sample_entries = list(pokemon_dict.items())[:5]
            print(f"Sample entries: {sample_entries}")
        except Exception as e:
            print(f"Error loading Pokemon names from CSV: {e}")
    else:
        print(f"CSV file '{POKEMON_NAMES_FILE}' not found.")
                
    return pokemon_dict

class PokemonQuizGame:
    def __init__(self):
        self.state = "start"  # "start", "game", "end"
        self.pokemon_images = []
        self.seen_pokemon = []
        self.skipped_pokemon = []  # Track skipped Pokémon separately
        self.current_pokemon = None
        self.start_time = 0
        self.time_left = TIMER_DURATION
        
        # Load Pokemon names
        self.pokemon_names = load_pokemon_names()
        
        # High score system
        self.high_score_manager = HighScoreManager()
        self.current_score = 0 # Final score for the round
        self.score = 0         # Running score during the game
        self.is_new_high_score = False
        self.first_interaction_done = False # Flag for initial state
        
        # Hard mode toggle
        self.hard_mode = False
        
        # Animated background
        self.gradient = AnimatedGradient(WINDOW_WIDTH, WINDOW_HEIGHT, [LIGHT_PINK, DARK_PINK])
        
        # Animation variables
        self.fade_alpha = 0
        self.fade_in = True
        self.pokemon_scale = 0.9
        self.scale_increasing = False
        
        # Pokemon list scroll variables
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_speed = 30
        
        # Buttons
        self.start_button = Button(
            WINDOW_WIDTH // 2 - 150, 
            WINDOW_HEIGHT // 5 + 150, 
            300, 80, "START", 
            GREEN, (100, 255, 100)
        )
        
        self.restart_button = Button(
            WINDOW_WIDTH // 2 - 150, 
            WINDOW_HEIGHT - 100, 
            300, 80, "PLAY AGAIN", 
            GREEN, (100, 255, 100)
        )
        
        self.scroll_up_button = Button(
            WINDOW_WIDTH - 80, 
            280, 
            60, 40, "▲", 
            GRAY, (150, 150, 150)
        )
        
        self.scroll_down_button = Button(
            WINDOW_WIDTH - 80, 
            WINDOW_HEIGHT - 180, 
            60, 40, "▼", 
            GRAY, (150, 150, 150)
        )
        
        # Hard mode checkbox
        self.hard_mode_checkbox = Checkbox(
            WINDOW_WIDTH // 2 - 80,
            WINDOW_HEIGHT // 5 + 250,
            240, 30, "Hard Mode",
            checked=False
        )
        
        # End screen hard mode checkbox
        self.end_hard_mode_checkbox = Checkbox(
            WINDOW_WIDTH // 2 - 80,
            WINDOW_HEIGHT - 130,
            240, 30, "Hard Mode",
            checked=False
        )
        
        # Load Pokemon images
        self.load_pokemon_images()
        
        # Game state variables
        self.reset_game()

    def reset_game(self):
        """Reset the game state for a new game"""
        self.seen_pokemon = []
        self.skipped_pokemon = []
        self.current_pokemon = None
        self.time_left = TIMER_DURATION
        self.score = 0
        self.current_score = 0
        self.is_new_high_score = False
        self.first_interaction_done = False
        self.state = "start"
        self.scroll_y = 0
        
        # Only reload images if they were cleared
        if not self.pokemon_images:
            self.load_pokemon_images()
            
        self.fade_alpha = 0
        self.fade_in = True
        self.pokemon_scale = 0.9
        self.scale_increasing = False
        
        # Make end screen checkbox match start screen checkbox
        self.end_hard_mode_checkbox.checked = self.hard_mode_checkbox.checked

    def load_pokemon_images(self):
        """Load all Pokemon images from the img directory"""
        image_dir = resource_path("img")
        print(f"Attempting to load images from: {image_dir}")
        
        if not os.path.exists(image_dir):
            print(f"Error: '{image_dir}' directory not found. Please create it and add Pokemon images.")
            return
        
        for filename in sorted(os.listdir(image_dir)):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                try:
                    image_path = os.path.join(image_dir, filename)
                    print(f"Loading image: {image_path}")
                    original_image = pygame.image.load(image_path)
                    
                    # Scale image to fit the screen while maintaining aspect ratio
                    scaled_image = self.scale_image(original_image)
                    
                    # Extract pokemon ID and name info
                    pokemon_id = self.get_pokemon_id_from_filename(filename)
                    
                    # Get the name directly from the dictionary
                    pokemon_name = "Unknown"
                    if pokemon_id in self.pokemon_names:
                        pokemon_name = self.pokemon_names[pokemon_id]
                    else:
                        print(f"WARNING: No name found for ID {pokemon_id}")
                    
                    # Store in our list (ID, name, image)
                    self.pokemon_images.append((pokemon_id, pokemon_name, scaled_image))
                    
                except pygame.error as e:
                    print(f"Could not load image {filename}: {e}")
        
        print(f"Loaded {len(self.pokemon_images)} Pokemon images")
        # Print first few entries as sample
        for i in range(min(5, len(self.pokemon_images))):
            pid, name, _ = self.pokemon_images[i]
            print(f"Loaded Pokemon {i+1}: ID={pid}, name={name}")

    def get_pokemon_id_from_filename(self, filename):
        """Extract Pokemon ID from filename"""
        parts = filename.split('.')
        base = parts[0]
        
        # Handle different filename formats (001.png or 001_Name.png)
        if '_' in base:
            id_part = base.split('_')[0]
        else:
            id_part = base
            
        # Ensure ID is consistently formatted (with leading zeros)
        formatted_id = id_part.zfill(3)
        print(f"Extracted ID '{formatted_id}' from filename '{filename}'")
        return formatted_id
    
    def get_pokemon_name(self, pokemon_id):
        """Get Pokemon name from ID, with nice formatting"""
        # Convert to string and ensure it has leading zeros (e.g., "1" -> "001")
        pokemon_num = str(pokemon_id).zfill(3)
        
        # Debug output
        print(f"Looking up Pokemon ID: '{pokemon_id}', formatted as '{pokemon_num}'")
        
        # Try to get from pokemon_names dictionary
        if pokemon_num in self.pokemon_names:
            name = self.pokemon_names[pokemon_num]
            print(f"Found name for {pokemon_num}: {name}")
            return name
        
        # Debug if not found
        print(f"Name not found for ID {pokemon_num}! Keys in dictionary: {list(self.pokemon_names.keys())[:5]}...")
        
        # Fallback to a more descriptive name if not found
        return f"Pokemon {pokemon_num}"

    def scale_image(self, image):
        """Scale image to fit the screen while maintaining aspect ratio"""
        max_width = WINDOW_WIDTH * 0.7
        max_height = WINDOW_HEIGHT * 0.7
        
        original_width, original_height = image.get_size()
        
        if original_width > max_width or original_height > max_height:
            scale_factor = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            return pygame.transform.scale(image, (new_width, new_height))
        
        return image

    def get_random_pokemon(self):
        """Get a random Pokemon that hasn't been seen yet"""
        if not self.pokemon_images:
            return None
        
        available_pokemon = [p for p in self.pokemon_images if p[0] not in self.seen_pokemon]
        
        if not available_pokemon:
            # If all Pokemon have been seen, reset the list
            self.seen_pokemon = []
            available_pokemon = self.pokemon_images
        
        return random.choice(available_pokemon)

    def start_game(self):
        """Start a new game"""
        self.state = "game"
        self.current_pokemon = self.get_random_pokemon()
        # Initialize lists and score/state variables
        self.seen_pokemon = []
        self.skipped_pokemon = []
        self.start_time = time.time()
        self.time_left = TIMER_DURATION
        self.is_new_high_score = False
        self.score = 0 # Start score at 0
        self.first_interaction_done = False # Reset flag
        
        # Set hard mode based on checkbox state
        self.hard_mode = self.hard_mode_checkbox.checked
        
        # Add the first pokemon to seen_pokemon
        if self.current_pokemon:
            pokemon_id = self.current_pokemon[0]
            self.seen_pokemon.append(pokemon_id)

    def next_pokemon(self):
        """Show the next Pokemon and score the previous one if not skipped."""
        # Score the pokemon that was just displayed, if interaction has happened
        # or if it's the very first interaction.
        if self.current_pokemon:
            previous_pokemon_id = self.current_pokemon[0]
            if not self.first_interaction_done:
                # This is the first SPACE press. Score the initial Pokemon.
                self.score += 1
                self.first_interaction_done = True
            elif previous_pokemon_id not in self.skipped_pokemon:
                # This is a subsequent SPACE press. Score if not skipped.
                self.score += 1
        
        # Get the next pokemon
        self.current_pokemon = self.get_random_pokemon()
        if self.current_pokemon:
            pokemon_id = self.current_pokemon[0]
            # Only add if not already in the list
            if pokemon_id not in self.seen_pokemon:
                self.seen_pokemon.append(pokemon_id)

    def skip_pokemon(self):
        """Skip the current Pokemon"""
        # Mark that the first interaction has occurred
        self.first_interaction_done = True
        
        if self.current_pokemon:
            # Add current Pokemon to skipped list if not already there
            pokemon_id = self.current_pokemon[0]
            if pokemon_id not in self.skipped_pokemon:
                self.skipped_pokemon.append(pokemon_id)
            
            # Get next Pokemon
            next_pokemon = self.get_random_pokemon()
            if next_pokemon:
                self.current_pokemon = next_pokemon
                
                # Only add to seen_pokemon if not already in the list
                pokemon_id = self.current_pokemon[0]
                if pokemon_id not in self.seen_pokemon:
                    self.seen_pokemon.append(pokemon_id)

    def end_game(self):
        """End the current game"""
        self.state = "end"
        
        # Check if the last pokemon displayed needs to be marked as skipped
        # because the timer ran out before the player acted on it.
        if self.current_pokemon:
            last_pokemon_id = self.current_pokemon[0]
            # Add to skipped list if not already there
            if last_pokemon_id not in self.skipped_pokemon:
                self.skipped_pokemon.append(last_pokemon_id)
            # Ensure it's also in the seen list (should be, but safe check)
            if last_pokemon_id not in self.seen_pokemon:
                self.seen_pokemon.append(last_pokemon_id)
                 
        # Set the final current_score for display and saving
        self.current_score = self.score
        
        # Reset scroll position
        self.scroll_y = 0
        
        # Sync hard mode checkbox state
        self.end_hard_mode_checkbox.checked = self.hard_mode
        
        # Check if this is a new high score
        top_score = self.high_score_manager.get_top_score()
        if self.current_score > top_score:
            self.is_new_high_score = True
        
        # Save the score
        self.high_score_manager.add_score(self.current_score)

    def update(self):
        """Update game state"""
        # Update the gradient animation
        self.gradient.update()
        
        if self.state == "game":
            # Update timer
            current_time = time.time()
            self.time_left = max(0, TIMER_DURATION - int(current_time - self.start_time))
            
            # End game if time runs out
            if self.time_left <= 0:
                self.end_game()
        
        # Update animations only if in hard mode or not in game state
        if self.hard_mode or self.state != "game":
            # Update fade animation
            if self.fade_in:
                self.fade_alpha = min(255, self.fade_alpha + 5)
                if self.fade_alpha >= 255:
                    self.fade_in = False
            else:
                self.fade_alpha = max(150, self.fade_alpha - 5)
                if self.fade_alpha <= 150:
                    self.fade_in = True
            
            # Update scale animation
            if self.scale_increasing:
                self.pokemon_scale = min(1.0, self.pokemon_scale + 0.005)
                if self.pokemon_scale >= 1.0:
                    self.scale_increasing = False
            else:
                self.pokemon_scale = max(0.9, self.pokemon_scale - 0.005)
                if self.pokemon_scale <= 0.9:
                    self.scale_increasing = True

    def handle_events(self):
        """Handle user input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # Quit on ESC
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Start game on Enter (from start screen)
                elif event.key == pygame.K_RETURN and self.state == "start":
                    self.start_game()
                
                # Next Pokemon on Space (during game)
                elif event.key == pygame.K_SPACE and self.state == "game":
                    self.next_pokemon()
                
                # Skip Pokemon on Backspace (during game)
                elif event.key == pygame.K_BACKSPACE and self.state == "game":
                    self.skip_pokemon()
                
                # Scroll list on end screen with arrow keys
                elif self.state == "end":
                    if event.key == pygame.K_UP:
                        self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                    elif event.key == pygame.K_DOWN:
                        self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check button clicks
                if self.state == "start":
                    if self.start_button.is_clicked():
                        self.start_game()
                    elif self.hard_mode_checkbox.is_clicked():
                        self.hard_mode_checkbox.toggle()
                
                elif self.state == "end":
                    if self.restart_button.is_clicked():
                        # Update hard mode from end screen
                        self.hard_mode_checkbox.checked = self.end_hard_mode_checkbox.checked
                        self.start_game()
                    elif self.end_hard_mode_checkbox.is_clicked():
                        self.end_hard_mode_checkbox.toggle()
                    elif self.scroll_up_button.is_clicked():
                        self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                    elif self.scroll_down_button.is_clicked():
                        self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
                    
                # Handle mouse wheel scrolling
                elif event.button == 4 and self.state == "end":  # Scroll up
                    self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                elif event.button == 5 and self.state == "end":  # Scroll down
                    self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
        
        return True

    def draw(self):
        """Draw the current game state to the screen"""
        # Draw animated background
        self.gradient.draw(screen)
        
        if self.state == "start":
            self.draw_start_screen()
        elif self.state == "game":
            self.draw_game_screen()
        elif self.state == "end":
            self.draw_end_screen()
        
        pygame.display.flip()

    def draw_start_screen(self):
        """Draw the start screen"""
        # Draw title - move down slightly from 1/4 to 1/5
        title_surf = title_font.render("Pokemon Quiz Game", True, BLACK)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 5))
        screen.blit(title_surf, title_rect)
        
        # Draw high score - reduce gap after title
        high_score = self.high_score_manager.get_top_score()
        high_score_surf = medium_font.render(f"High Score: {high_score}", True, BLACK)
        high_score_rect = high_score_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 5 + 70))
        screen.blit(high_score_surf, high_score_rect)
        
        # Draw start button - move up
        self.start_button.draw(screen)
        
        # Draw hard mode checkbox
        self.hard_mode_checkbox.draw(screen)
        
        # Draw instructions - move up
        instructions = [
            "How to play:",
            "1. Press SPACE to cycle through Pokemon",
            "2. Press BACKSPACE to skip Pokemon you don't know",
            "3. Try to name as many Pokemon as you can in 60 seconds",
            "4. Press ESC to quit"
        ]
        
        for i, text in enumerate(instructions):
            instr_surf = small_font.render(text, True, BLACK)
            instr_rect = instr_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2/3 + i * 40))
            screen.blit(instr_surf, instr_rect)

    def draw_game_screen(self):
        """Draw the game screen with Pokemon and timer"""
        # Draw timer with color based on time left
        timer_color = GREEN if self.time_left > 10 else RED
        timer_surf = large_font.render(f"Time: {self.time_left}", True, timer_color)
        timer_rect = timer_surf.get_rect(center=(WINDOW_WIDTH // 2, 40))
        screen.blit(timer_surf, timer_rect)
        
        # Draw current score
        count_surf = medium_font.render(f"Score: {self.score}", True, BLACK)
        count_rect = count_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40))
        screen.blit(count_surf, count_rect)
        
        # Draw high score
        high_score = self.high_score_manager.get_top_score()
        high_score_surf = small_font.render(f"High Score: {high_score}", True, BLACK)
        high_score_rect = high_score_surf.get_rect(topleft=(20, 20))
        screen.blit(high_score_surf, high_score_rect)
        
        # Draw hard mode indicator if enabled
        if self.hard_mode:
            hard_mode_surf = small_font.render("Hard Mode", True, RED)
            hard_mode_rect = hard_mode_surf.get_rect(topright=(WINDOW_WIDTH - 20, 20))
            screen.blit(hard_mode_surf, hard_mode_rect)
        
        # Draw current Pokemon with animation
        if self.current_pokemon:
            pokemon_id, pokemon_name, pokemon_image = self.current_pokemon
            
            # Apply scaling animation if hard mode is enabled, otherwise just display at 100% scale
            if self.hard_mode:
                current_width, current_height = pokemon_image.get_size()
                scaled_width = int(current_width * self.pokemon_scale)
                scaled_height = int(current_height * self.pokemon_scale)
                animated_image = pygame.transform.scale(pokemon_image, (scaled_width, scaled_height))
            else:
                animated_image = pokemon_image
            
            # Center the image
            image_rect = animated_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(animated_image, image_rect)
            
            # Draw semi-transparent "SPACE for next" text
            hint_surf = small_font.render("Press SPACE for next Pokemon | BACKSPACE to skip", True, BLACK)
            hint_surf.set_alpha(self.fade_alpha if self.hard_mode else 200)  # Constant alpha if not hard mode
            hint_rect = hint_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
            screen.blit(hint_surf, hint_rect)

    def draw_end_screen(self):
        """Draw the end screen with results"""
        # Draw header
        header_surf = title_font.render("Time's Up!", True, RED)
        header_rect = header_surf.get_rect(center=(WINDOW_WIDTH // 2, 60))
        screen.blit(header_surf, header_rect)
        
        # Calculate stats
        total_seen = len(self.seen_pokemon)
        total_skipped = len(self.skipped_pokemon)
        
        # Draw stats
        stats_surf = large_font.render(f"Score: {self.current_score}", True, BLACK)
        stats_rect = stats_surf.get_rect(center=(WINDOW_WIDTH // 2, 120))
        screen.blit(stats_surf, stats_rect)
        
        # Draw additional stats
        seen_text = f"Total Pokémon seen: {total_seen} (Skipped: {total_skipped})"
        seen_surf = medium_font.render(seen_text, True, BLACK)
        seen_rect = seen_surf.get_rect(center=(WINDOW_WIDTH // 2, 170))
        screen.blit(seen_surf, seen_rect)
        
        # Draw high score
        high_score = self.high_score_manager.get_top_score()
        high_score_text = f"High Score: {high_score}"
        high_score_color = GOLD if self.is_new_high_score else BLACK
        
        if self.is_new_high_score:
            high_score_text = f"New High Score: {high_score}!"
        
        high_score_surf = medium_font.render(high_score_text, True, high_score_color)
        high_score_rect = high_score_surf.get_rect(center=(WINDOW_WIDTH // 2, 220))
        screen.blit(high_score_surf, high_score_rect)
        
        # Draw hard mode checkbox (moved above restart button for visibility)
        self.end_hard_mode_checkbox.draw(screen)
        
        # Draw restart button
        self.restart_button.draw(screen)
        
        # Draw list of seen Pokemon - position lower to add more space
        list_title_surf = medium_font.render("Pokemon You Saw:", True, BLACK)
        list_title_rect = list_title_surf.get_rect(center=(WINDOW_WIDTH // 2, 290))
        screen.blit(list_title_surf, list_title_rect)
        
        # Create the scrollable list view
        self.draw_scrollable_pokemon_list()

    def draw_scrollable_pokemon_list(self):
        """Draw a scrollable grid of seen Pokemon in the order they appeared"""
        # Set up list area dimensions - position lower to add space after title
        list_area_x = 80
        list_area_y = 320  # Increased from 280 to add space after title
        list_area_width = WINDOW_WIDTH - 160  # Leave margins on both sides
        list_area_height = WINDOW_HEIGHT - list_area_y - 140  # Leave space for restart button
        
        # Create a clipping rect for the list area
        list_area_rect = pygame.Rect(list_area_x, list_area_y, list_area_width, list_area_height)
        pygame.draw.rect(screen, (255, 255, 255, 100), list_area_rect, border_radius=10)
        
        # Get Pokemon info in the order they were seen
        seen_pokemon_info = []
        for pokemon_id in self.seen_pokemon:
            # Find this pokemon in our loaded pokemon_images list to get its cached name
            pokemon_name = None
            for pid, name, _ in self.pokemon_images:
                if pid == pokemon_id:
                    pokemon_name = name
                    break
            
            # Fallback if not found (shouldn't happen)
            if pokemon_name is None:
                pokemon_name = f"Pokemon {pokemon_id}"
                
            is_skipped = pokemon_id in self.skipped_pokemon
            seen_pokemon_info.append((pokemon_id, pokemon_name, is_skipped))
        
        # Debug output for the first few Pokemon names
        if seen_pokemon_info:
            for i in range(min(5, len(seen_pokemon_info))):
                pid, entry, skipped = seen_pokemon_info[i]
                print(f"Debug - Pokemon {i+1}: ID={pid}, entry={entry}, skipped={skipped}")
        
        # Calculate grid layout - increase item_width for better spacing
        item_height = 30
        item_width = 250  # Increased from 200 to provide more space
        items_per_row = max(1, list_area_width // item_width)
        
        # Ensure even spacing between columns
        total_items_width = items_per_row * item_width
        horizontal_spacing = (list_area_width - total_items_width) // (items_per_row + 1)
        
        # Calculate total content height for scrolling
        total_rows = math.ceil(len(seen_pokemon_info) / items_per_row)
        total_content_height = total_rows * (item_height + 10)  # 10px vertical gap
        self.max_scroll = max(0, total_content_height - list_area_height)
        
        # Create a clipping mask to only show items within the list area
        original_clip = screen.get_clip()
        screen.set_clip(list_area_rect)
        
        # Draw each Pokemon entry in a grid layout
        for i, (pokemon_id, pokemon_entry, is_skipped) in enumerate(seen_pokemon_info):
            row = i // items_per_row
            col = i % items_per_row
            
            # Calculate position (with scrolling offset)
            x = list_area_x + horizontal_spacing + col * (item_width + horizontal_spacing)
            y = list_area_y + 10 + row * (item_height + 10) - self.scroll_y
            
            # Only draw if visible in the viewport
            if list_area_y - item_height <= y <= list_area_y + list_area_height:
                # Use red color for skipped Pokemon
                text_color = RED if is_skipped else BLACK
                
                # Format as "#ID. Name" for clarity and conciseness
                display_text = f"#{pokemon_id}. {pokemon_entry}"
                
                # Print debug info for the first few items
                if i < 5:
                    print(f"Rendering Pokemon {i+1}: {display_text}")
                
                pokemon_surf = small_font.render(display_text, True, text_color)
                screen.blit(pokemon_surf, (x, y))
        
        # Reset the clipping mask
        screen.set_clip(original_clip)
        
        # Draw scroll buttons if needed
        if self.max_scroll > 0:
            self.scroll_up_button.draw(screen)
            self.scroll_down_button.draw(screen)
            
            # Draw scroll indicator (optional)
            if self.max_scroll > 0:
                scroll_percent = self.scroll_y / self.max_scroll
                indicator_height = max(30, list_area_height * (list_area_height / total_content_height))
                indicator_y = list_area_y + (list_area_height - indicator_height) * scroll_percent
                
                indicator_rect = pygame.Rect(WINDOW_WIDTH - 50, indicator_y, 10, indicator_height)
                pygame.draw.rect(screen, GRAY, indicator_rect, border_radius=5)

    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        # Ensure Pokemon names are loaded at startup
        if not self.pokemon_names:
            print("Pokemon names dictionary is empty - reloading from CSV...")
            self.pokemon_names = load_pokemon_names()
        
        # Ensure Pokemon images are loaded at startup
        if not self.pokemon_images:
            print("Pokemon images list is empty - reloading images...")
            self.load_pokemon_images()
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            clock.tick(FPS)
        
        # Ensure high scores are saved when closing
        print("Game closing - saving high scores...")
        self.high_score_manager.save_high_scores()
        
        pygame.quit()

if __name__ == "__main__":
    game = PokemonQuizGame()
    game.run() 