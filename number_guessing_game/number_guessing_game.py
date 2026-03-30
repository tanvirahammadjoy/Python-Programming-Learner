"""
Advanced Number Guessing Game
A comprehensive guessing game with difficulty levels, hints, scoring, and leaderboard.
"""

import random
import time
import os

class NumberGuessingGame:
    """Main game class handling all game functionality"""
    
    def __init__(self):
        """Initialize the game with default settings"""
        self.difficulty_settings = {
            'easy': {'min': 1, 'max': 50, 'name': 'Easy'},
            'medium': {'min': 1, 'max': 100, 'name': 'Medium'},
            'hard': {'min': 1, 'max': 200, 'name': 'Hard'}
        }
        self.current_difficulty = 'medium'
        self.secret_number = None
        self.attempts = 0
        self.max_attempts = None
        self.start_time = None
        self.end_time = None
        self.leaderboard_file = 'leaderboard.txt'
        self.guess_history = []
        self.hint_given = False
        
    def display_welcome(self):
        """Display welcome message and game rules"""
        print("\n" + "="*50)
        print("🎲 ADVANCED NUMBER GUESSING GAME 🎲".center(50))
        print("="*50)
        print("\n🎮 How to Play:")
        print("• Guess the secret number within the range")
        print("• Get hints after 3 wrong guesses")
        print("• Earn points based on attempts and time")
        print("• Try to make it to the leaderboard!\n")
        
    def choose_difficulty(self):
        """Let player choose difficulty level"""
        while True:
            print("\n📊 DIFFICULTY LEVELS:")
            print("1. Easy (1-50)")
            print("2. Medium (1-100)")
            print("3. Hard (1-200)")
            
            choice = input("\nChoose difficulty (1/2/3): ").strip()
            
            if choice == '1':
                self.current_difficulty = 'easy'
                break
            elif choice == '2':
                self.current_difficulty = 'medium'
                break
            elif choice == '3':
                self.current_difficulty = 'hard'
                break
            else:
                print("❌ Invalid choice! Please enter 1, 2, or 3.")
        
        settings = self.difficulty_settings[self.current_difficulty]
        print(f"\n✅ Difficulty set to {settings['name']}!")
        print(f"📏 Number range: {settings['min']} to {settings['max']}")
        
    def generate_secret_number(self):
        """Generate random secret number based on difficulty"""
        settings = self.difficulty_settings[self.current_difficulty]
        self.secret_number = random.randint(settings['min'], settings['max'])
        self.attempts = 0
        self.guess_history = []
        self.hint_given = False
        
    def provide_hint(self):
        """Provide a helpful hint based on the secret number"""
        if self.hint_given:
            return
        
        remaining_range = self.difficulty_settings[self.current_difficulty]
        
        # Different types of hints
        hint_type = random.choice(['parity', 'range', 'multiple'])
        
        if hint_type == 'parity':
            hint = f"💡 Hint: The number is {'even' if self.secret_number % 2 == 0 else 'odd'}!"
        elif hint_type == 'multiple':
            hint = f"💡 Hint: The number is a multiple of {self.secret_number % 10 or 10}!"
        else:  # range hint
            # Narrow down the range
            lower_bound = max(remaining_range['min'], self.secret_number - 20)
            upper_bound = min(remaining_range['max'], self.secret_number + 20)
            hint = f"💡 Hint: The number is between {lower_bound} and {upper_bound}!"
        
        print(hint)
        self.hint_given = True
        
    def get_player_guess(self):
        """Get and validate player's guess"""
        settings = self.difficulty_settings[self.current_difficulty]
        
        while True:
            try:
                guess = input(f"\nAttempt {self.attempts + 1}: Enter your guess ({settings['min']}-{settings['max']}): ")
                guess = int(guess)
                
                if guess < settings['min'] or guess > settings['max']:
                    print(f"⚠️ Please enter a number between {settings['min']} and {settings['max']}!")
                    continue
                    
                return guess
                
            except ValueError:
                print("❌ Invalid input! Please enter a valid number.")
                
    def check_guess(self, guess):
        """Check guess and provide feedback"""
        self.attempts += 1
        self.guess_history.append(guess)
        
        if guess < self.secret_number:
            print("📈 Too low! 🔼")
            return False
        elif guess > self.secret_number:
            print("📉 Too high! 🔽")
            return False
        else:
            print(f"\n🎉 CORRECT! You guessed it in {self.attempts} attempts!")
            return True
            
    def calculate_score(self):
        """Calculate score based on difficulty, attempts, and time"""
        base_scores = {'easy': 100, 'medium': 200, 'hard': 300}
        base_score = base_scores[self.current_difficulty]
        
        # Time bonus
        time_taken = self.end_time - self.start_time
        time_bonus = max(0, 100 - int(time_taken / 2))
        
        # Attempts penalty
        attempt_penalty = (self.attempts - 1) * 5
        
        score = base_score + time_bonus - attempt_penalty
        return max(0, score), time_taken
        
    def save_to_leaderboard(self, player_name, score, time_taken):
        """Save player's score to leaderboard file"""
        try:
            # Read existing scores
            scores = []
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            scores.append(line.strip().split('|'))
            
            # Add new score
            scores.append([player_name, str(score), f"{time_taken:.1f}s", 
                          self.difficulty_settings[self.current_difficulty]['name']])
            
            # Sort by score (highest first)
            scores.sort(key=lambda x: int(x[1]), reverse=True)
            
            # Keep top 10
            scores = scores[:10]
            
            # Write back to file
            with open(self.leaderboard_file, 'w') as f:
                f.write("PLAYER|SCORE|TIME|DIFFICULTY\n")
                for s in scores:
                    f.write(f"{s[0]}|{s[1]}|{s[2]}|{s[3]}\n")
                    
            return True
        except Exception as e:
            print(f"Error saving to leaderboard: {e}")
            return False
            
    def display_leaderboard(self):
        """Display the leaderboard"""
        if not os.path.exists(self.leaderboard_file):
            print("\n📊 No scores yet! Be the first to play!")
            return
            
        try:
            print("\n" + "="*60)
            print("🏆 LEADERBOARD 🏆".center(60))
            print("="*60)
            print(f"{'Player':<15} {'Score':<8} {'Time':<10} {'Difficulty':<10}")
            print("-"*60)
            
            with open(self.leaderboard_file, 'r') as f:
                next(f)  # Skip header
                for line in f:
                    if line.strip():
                        player, score, time_taken, difficulty = line.strip().split('|')
                        print(f"{player:<15} {score:<8} {time_taken:<10} {difficulty:<10}")
                        
        except Exception as e:
            print(f"Error reading leaderboard: {e}")
            
    def play_round(self):
        """Play one complete round"""
        self.generate_secret_number()
        self.start_time = time.time()
        
        settings = self.difficulty_settings[self.current_difficulty]
        print(f"\n🎯 Game started! Guess the number between {settings['min']} and {settings['max']}")
        print("Type 'hint' for a hint (after 3 attempts), 'quit' to exit\n")
        
        while True:
            # Check if hint should be offered
            if self.attempts == 3 and not self.hint_given:
                print("\n🔍 Hint available! Type 'hint' to get a clue")
            
            # Get input (supports hints and quit)
            user_input = input(f"\nAttempt {self.attempts + 1}: ").strip().lower()
            
            if user_input == 'quit':
                print(f"\n👋 Game abandoned! The number was {self.secret_number}")
                return False
            elif user_input == 'hint':
                if self.attempts >= 3:
                    self.provide_hint()
                else:
                    print(f"💡 Hints are available after 3 attempts! ({self.attempts}/3)")
                continue
            
            # Process as guess
            try:
                guess = int(user_input)
                if guess < settings['min'] or guess > settings['max']:
                    print(f"⚠️ Please enter a number between {settings['min']} and {settings['max']}!")
                    continue
                    
                if self.check_guess(guess):
                    self.end_time = time.time()
                    return True
                    
            except ValueError:
                print("❌ Invalid input! Please enter a number, 'hint', or 'quit'.")
                
    def display_summary(self):
        """Display game summary after winning"""
        score, time_taken = self.calculate_score()
        
        print("\n" + "="*50)
        print("📊 GAME SUMMARY".center(50))
        print("="*50)
        print(f"🎯 Secret Number: {self.secret_number}")
        print(f"📝 Total Attempts: {self.attempts}")
        print(f"⏱️ Time Taken: {time_taken:.2f} seconds")
        print(f"⭐ Score: {score} points")
        print(f"📈 Guess History: {self.guess_history}")
        print("="*50)
        
        # Save to leaderboard
        if score > 0:
            player_name = input("\n🏆 Enter your name for the leaderboard: ").strip()
            if player_name:
                self.save_to_leaderboard(player_name, score, time_taken)
                print(f"✅ Score saved! {player_name} earned {score} points!")
                
    def run(self):
        """Main game loop"""
        self.display_welcome()
        
        while True:
            self.choose_difficulty()
            
            if self.play_round():
                self.display_summary()
            else:
                print("\n💔 Better luck next time!")
            
            # Show leaderboard
            self.display_leaderboard()
            
            # Ask to play again
            play_again = input("\n🎮 Would you like to play again? (y/n): ").strip().lower()
            if play_again != 'y':
                print("\n👋 Thanks for playing! Goodbye!")
                break


# Entry point
if __name__ == "__main__":
    game = NumberGuessingGame()
    game.run()
