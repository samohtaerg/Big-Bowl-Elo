# -*- coding: utf-8 -*-
"""Restaurant Dish Ranking System using Elo Ratings"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import random
import json
import os
from itertools import combinations

# Set Chinese font for matplotlib
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display issue

class RestaurantEloSystem:
    def __init__(self, menu_file="menu_names.txt", save_file="elo_ratings.json"):
        self.menu_file = menu_file
        self.save_file = save_file
        self.load_menu()
        self.load_ratings()
    
    def load_menu(self):
        """Load menu from text file"""
        self.menu = []
        encodings_to_try = ['utf-8-sig', 'utf-8', 'gb2312', 'gbk', 'cp936']
        
        for encoding in encodings_to_try:
            try:
                with open(self.menu_file, 'r', encoding=encoding) as f:
                    self.menu = []
                    for line in f:
                        line = line.strip()
                        if '→' in line:
                            dish_name = line.split('→')[1].strip()
                            if dish_name:
                                self.menu.append(dish_name)
                if len(self.menu) > 0:
                    print(f"Successfully loaded {len(self.menu)} dishes using {encoding} encoding")
                    break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if len(self.menu) == 0:
            print("Warning: Could not load dishes with any encoding. Creating sample menu.")
            # Create a sample menu for testing
            self.menu = [
                "独家大碗米粉", "猪骨汤米线", "番茄汤米线", "沙爹米线", "泡椒酸米线",
                "酸菜麻辣米线", "双椒麻辣米线", "盐酥鸡", "港式叉烧云吞汤面", "咖喱鱼丸",
                "麻辣酸菜牛腩汤米线", "麻辣牛腩牛腱牛百叶汤米线", "港式西多士", "滑蛋叉烧饭", "卤肉饭"
            ]
            print(f"Using sample menu with {len(self.menu)} dishes")
    
    def load_ratings(self):
        """Load existing Elo ratings or initialize new ones"""
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.elo = data.get('elo', {})
                self.games_played = data.get('games_played', {})
            print(f"Loaded existing ratings for {len(self.elo)} dishes")
        else:
            self.elo = {}
            self.games_played = {}
            print("Initialized new rating system")
        
        # Don't initialize dishes that haven't played - only add them when they actually play
    
    def save_ratings(self):
        """Save current Elo ratings to file"""
        data = {
            'elo': self.elo,
            'games_played': self.games_played
        }
        with open(self.save_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved ratings to {self.save_file}")
    
    def select_random_dishes(self, n=5):
        """Select n random dishes from menu"""
        return random.sample(self.menu, n)
    
    def generate_pairwise_comparisons(self, dishes):
        """Generate all possible pairwise combinations"""
        return list(combinations(dishes, 2))
    
    def mock_comparison_result(self, dish1, dish2):
        """Mock comparison result based on current Elo ratings with some randomness"""
        # Get ratings, default to 1500 if dish hasn't played before
        rating1 = self.elo.get(dish1, 1500)
        rating2 = self.elo.get(dish2, 1500)
        
        # Calculate expected probability for dish1 to win
        expected1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))
        
        # Add some randomness - higher rated dish has better chance but not guaranteed
        random_factor = random.random()
        
        # 70% based on Elo expectation, 30% pure randomness
        if random_factor < (0.7 * expected1 + 0.15):
            return dish1  # dish1 wins
        else:
            return dish2  # dish2 wins
    
    def update_elo(self, winner, loser, k=32):
        """Update Elo ratings after a match"""
        # Initialize dishes if this is their first match
        if winner not in self.elo:
            self.elo[winner] = 1500
            self.games_played[winner] = 0
        if loser not in self.elo:
            self.elo[loser] = 1500
            self.games_played[loser] = 0
            
        Ra, Rb = self.elo[winner], self.elo[loser]
        Ea = 1 / (1 + 10 ** ((Rb - Ra) / 400))
        Eb = 1 - Ea
        
        self.elo[winner] = Ra + k * (1 - Ea)
        self.elo[loser] = Rb + k * (0 - Eb)
        
        self.games_played[winner] += 1
        self.games_played[loser] += 1
    
    def run_iteration(self, iteration_num):
        """Run one iteration with 5 dishes and all pairwise comparisons"""
        print(f"\n=== ITERATION {iteration_num} ===")
        
        # Select 5 random dishes
        selected_dishes = self.select_random_dishes(5)
        print(f"Selected dishes: {selected_dishes}")
        
        # Generate all pairwise comparisons (10 total)
        pairs = self.generate_pairwise_comparisons(selected_dishes)
        print(f"Generated {len(pairs)} pairwise comparisons")
        
        # Mock comparison results and update Elo
        results = []
        for dish1, dish2 in pairs:
            winner = self.mock_comparison_result(dish1, dish2)
            loser = dish2 if winner == dish1 else dish1
            
            old_elo_winner = self.elo.get(winner, 1500)
            old_elo_loser = self.elo.get(loser, 1500)
            
            self.update_elo(winner, loser)
            
            results.append({
                'winner': winner,
                'loser': loser,
                'winner_elo_change': self.elo[winner] - old_elo_winner,
                'loser_elo_change': self.elo[loser] - old_elo_loser
            })
        
        # Print results
        print("\nComparison Results:")
        for result in results:
            print(f"  {result['winner']} beat {result['loser']} "
                  f"(+{result['winner_elo_change']:.1f} / {result['loser_elo_change']:.1f})")
        
        return selected_dishes, results
    
    def generate_ranking_report(self):
        """Generate official and provisional rankings"""
        # Split into official vs provisional
        official = [(dish, score, self.games_played[dish]) 
                   for dish, score in self.elo.items() 
                   if self.games_played[dish] >= 3]
        
        provisional = [(dish, score, self.games_played[dish]) 
                      for dish, score in self.elo.items() 
                      if 0 < self.games_played[dish] < 3]
        
        # Create DataFrames
        official_df = pd.DataFrame(official, columns=["Dish", "Elo Score", "Games Played"])
        official_df = official_df.sort_values(by="Elo Score", ascending=False)
        
        provisional_df = pd.DataFrame(provisional, columns=["Dish", "Elo Score", "Games Played"])
        provisional_df = provisional_df.sort_values(by="Elo Score", ascending=False)
        
        return official_df, provisional_df
    
    def plot_rankings(self, iteration_num, save_plot=True):
        """Create and display/save ranking visualization"""
        official_df, provisional_df = self.generate_ranking_report()
        
        total_dishes = len(official_df) + len(provisional_df)
        fig_height = max(6, total_dishes * 0.5 + 2)  # More space for each dish
        plt.figure(figsize=(16, fig_height))  # Wider figure
        
        # Combine for plotting (official on top, provisional below)
        y_pos_official = range(len(official_df))
        y_pos_provisional = range(len(official_df), len(official_df) + len(provisional_df))
        
        # Find max Elo score for setting text position
        max_elo = 1600  # Default max
        if not official_df.empty:
            max_elo = max(max_elo, official_df["Elo Score"].max())
        if not provisional_df.empty:
            max_elo = max(max_elo, provisional_df["Elo Score"].max())
        
        # Plot official (orange)
        if not official_df.empty:
            bars_official = plt.barh(y_pos_official, official_df["Elo Score"], 
                                   color="orange", label="Official (3+ games)", alpha=0.8)
            
            # Add text labels inside bars and ranking numbers after bars
            for i, (idx, row) in enumerate(official_df.iterrows()):
                # Dish name inside bar
                plt.text(row["Elo Score"] * 0.02, i, 
                        f"{row['Dish']} ({row['Games Played']} games)", 
                        va='center', ha='left', fontsize=9, color='white', weight='bold')
                
                # Elo score after bar
                plt.text(row["Elo Score"] + max_elo * 0.02, i, 
                        f"{row['Elo Score']:.0f}", 
                        va='center', ha='left', fontsize=10, color='black', weight='bold')
        
        # Plot provisional (gray)
        if not provisional_df.empty:
            bars_provisional = plt.barh(y_pos_provisional, provisional_df["Elo Score"], 
                                      color="gray", label="Provisional (<3 games)", alpha=0.6)
            
            # Add text labels inside bars and ranking numbers after bars
            for i, (idx, row) in enumerate(provisional_df.iterrows()):
                # Dish name inside bar
                plt.text(row["Elo Score"] * 0.02, i + len(official_df), 
                        f"{row['Dish']} ({row['Games Played']} games)", 
                        va='center', ha='left', fontsize=9, color='white', weight='bold')
                
                # Elo score after bar
                plt.text(row["Elo Score"] + max_elo * 0.02, i + len(official_df), 
                        f"{row['Elo Score']:.0f}", 
                        va='center', ha='left', fontsize=10, color='gray', weight='bold')
        
        plt.gca().invert_yaxis()
        plt.title(f"Da Wan Gong Restaurant - Dish Elo Ranking (After Iteration {iteration_num})", 
                 fontsize=14, pad=20)
        plt.xlabel("Elo Score", fontsize=12)
        
        # Move legend to bottom with more space
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=10)
        
        # Remove y-axis labels since we have text on bars
        plt.gca().set_yticks([])
        
        # Set x-axis limits to prevent text overflow and leave space for ranking numbers
        plt.xlim(0, max_elo * 1.15)
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig(f"ranking_iteration_{iteration_num}.png", dpi=150, bbox_inches='tight')
            print(f"Plot saved as ranking_iteration_{iteration_num}.png")
        
        plt.show()
        
        return official_df, provisional_df

def main():
    # Initialize the system
    system = RestaurantEloSystem()
    
    # Run two iterations as requested
    for iteration in [1, 2]:
        selected_dishes, results = system.run_iteration(iteration)
        
        # Generate and display rankings
        official_df, provisional_df = system.plot_rankings(iteration)
        
        print(f"\n=== RANKINGS AFTER ITERATION {iteration} ===")
        print("Official Ranking (3+ games):")
        print(official_df.to_string(index=False) if not official_df.empty else "No dishes with 3+ games yet")
        
        print("\nProvisional Ranking (<3 games):")
        print(provisional_df.to_string(index=False) if not provisional_df.empty else "No provisional dishes")
        
        # Save ratings after each iteration
        system.save_ratings()
        
        print(f"\nIteration {iteration} completed!")
    
    # Add a demonstration of provisional ranking - simulate some individual matches
    print("\n=== ADDING SOME INDIVIDUAL MATCHES TO SHOW PROVISIONAL RANKING ===")
    
    # Add a few random individual matches to create dishes with 1-2 games
    new_dishes = ["番茄汤米线", "沙爹米线", "盐酥鸡"]
    for i, new_dish in enumerate(new_dishes):
        # Pick a random existing dish to compete against
        existing_dishes = list(system.elo.keys())
        opponent = system.select_random_dishes(1)[0] if len(existing_dishes) > 0 else "独家大碗米粉"
        
        # Simulate 1-2 matches for each new dish
        matches_to_play = i + 1  # 1, 2, 3 matches respectively
        for match_num in range(matches_to_play):
            winner = system.mock_comparison_result(new_dish, opponent)
            loser = opponent if winner == new_dish else new_dish
            system.update_elo(winner, loser)
            print(f"Individual match: {winner} beat {loser}")
    
    # Generate final ranking with provisional dishes
    official_df, provisional_df = system.plot_rankings("Final")
    
    print(f"\n=== FINAL RANKINGS WITH PROVISIONAL DISHES ===")
    print("Official Ranking (3+ games):")
    print(official_df.to_string(index=False) if not official_df.empty else "No dishes with 3+ games yet")
    
    print("\nProvisional Ranking (<3 games):")
    print(provisional_df.to_string(index=False) if not provisional_df.empty else "No provisional dishes")
    
    system.save_ratings()

if __name__ == "__main__":
    main()