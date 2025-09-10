# -*- coding: utf-8 -*-
"""
Consolidate ELO data to fix duplicate dishes and calculate correct ratings
"""

import json
import pandas as pd
from datetime import datetime

def extract_chinese_name(dish_name):
    """Extract Chinese name from dish name, handling both formats"""
    if ' | ' in dish_name:
        return dish_name.split(' | ')[0].strip()
    return dish_name.strip()

def consolidate_elo_data():
    """Consolidate duplicate dish entries and recalculate ELO ratings"""
    
    # Load the exported data
    with open('elo_data_20250910_195224.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    elo_ratings = data['elo_ratings']
    games_played = data['games_played']
    battle_history = data['battle_history']
    
    print(f"Original data: {len(elo_ratings)} dish entries, {len(battle_history)} battles")
    
    # Create mapping from all names to Chinese names
    dish_mapping = {}
    chinese_names = set()
    
    for dish_name in elo_ratings.keys():
        chinese_name = extract_chinese_name(dish_name)
        dish_mapping[dish_name] = chinese_name
        chinese_names.add(chinese_name)
    
    print(f"Found {len(chinese_names)} unique dishes after consolidation")
    
    # Consolidate ELO ratings and games
    consolidated_elo = {}
    consolidated_games = {}
    
    for chinese_name in chinese_names:
        # Find all variants of this dish
        variants = [dish for dish in elo_ratings.keys() if extract_chinese_name(dish) == chinese_name]
        
        if len(variants) == 1:
            # Single variant - use as is
            dish = variants[0]
            consolidated_elo[chinese_name] = elo_ratings[dish]
            consolidated_games[chinese_name] = games_played[dish]
        else:
            # Multiple variants - need to merge
            print(f"Merging variants for {chinese_name}: {variants}")
            
            # Find the variant with the most games played (most recent data)
            best_variant = max(variants, key=lambda d: games_played.get(d, 0))
            
            # Use the ELO from the most active variant
            consolidated_elo[chinese_name] = elo_ratings[best_variant]
            
            # Sum up all games played
            total_games = sum(games_played.get(variant, 0) for variant in variants)
            consolidated_games[chinese_name] = total_games
            
            print(f"  Using ELO {elo_ratings[best_variant]:.1f} from {best_variant}, total games: {total_games}")
    
    # Update battle history to use Chinese names
    updated_battle_history = []
    for battle in battle_history:
        updated_battle = battle.copy()
        updated_battle['winner'] = extract_chinese_name(battle['winner'])
        updated_battle['loser'] = extract_chinese_name(battle['loser'])
        updated_battle_history.append(updated_battle)
    
    # Calculate total battles for verification
    battle_counts = {}
    for battle in updated_battle_history:
        winner = battle['winner']
        loser = battle['loser']
        battle_counts[winner] = battle_counts.get(winner, 0) + 1
        battle_counts[loser] = battle_counts.get(loser, 0) + 1
    
    print(f"\nBattle count verification:")
    for dish in sorted(consolidated_games.keys()):
        calculated_battles = battle_counts.get(dish, 0)
        stored_battles = consolidated_games[dish]
        status = "OK" if calculated_battles == stored_battles else "MISMATCH"
        print(f"{status} {dish}: stored={stored_battles}, calculated={calculated_battles}")
    
    total_battles = len(updated_battle_history)
    print(f"\nTotal battles: {total_battles}")
    
    # Create consolidated data structure
    consolidated_data = {
        'elo': consolidated_elo,
        'games_played': consolidated_games,
        'last_updated': datetime.now().isoformat()
    }
    
    # Save consolidated ratings
    with open('elo_ratings.json', 'w', encoding='utf-8') as f:
        json.dump(consolidated_data, f, ensure_ascii=False, indent=2)
    
    # Save consolidated battle history
    with open('battle_history.json', 'w', encoding='utf-8') as f:
        json.dump(updated_battle_history, f, ensure_ascii=False, indent=2)
    
    print(f"\nConsolidation complete!")
    print(f"Final stats: {len(consolidated_elo)} dishes, {total_battles} battles")
    
    # Display final rankings
    print(f"\nFinal Rankings:")
    
    # Sort by ELO score
    sorted_dishes = sorted(consolidated_elo.items(), key=lambda x: x[1], reverse=True)
    
    official_dishes = [(dish, score) for dish, score in sorted_dishes if consolidated_games[dish] >= 3]
    provisional_dishes = [(dish, score) for dish, score in sorted_dishes if consolidated_games[dish] < 3]
    
    print(f"\nOfficial Ranking ({len(official_dishes)} dishes with 3+ games):")
    for i, (dish, score) in enumerate(official_dishes, 1):
        games = consolidated_games[dish]
        print(f"#{i:2d} {dish:<30} {score:4.0f} ({games} games)")
    
    print(f"\nProvisional Ranking ({len(provisional_dishes)} dishes with <3 games):")
    for i, (dish, score) in enumerate(provisional_dishes, 1):
        games = consolidated_games[dish]
        print(f"#{i:2d} {dish:<30} {score:4.0f} ({games} games)")
    
    return consolidated_data, updated_battle_history

if __name__ == "__main__":
    consolidate_elo_data()