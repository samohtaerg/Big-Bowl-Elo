# -*- coding: utf-8 -*-
"""Streamlit Web App for Restaurant Dish Ranking System"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import json
import os
import re
import io
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set Chinese font for matplotlib
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class StreamlitEloSystem:
    def __init__(self, save_file="elo_ratings.json"):
        self.save_file = save_file
        self.load_existing_ratings()
    
    def load_existing_ratings(self):
        """Load existing Elo ratings or initialize new ones"""
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.elo = data.get('elo', {})
                self.games_played = data.get('games_played', {})
        else:
            self.elo = {}
            self.games_played = {}
    
    def parse_match_content(self, content):
        """Parse match results from file content"""
        matches = []
        lines = content.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('Pairwise比较') or line.startswith('比较'):
                continue
            
            # Use regex to find pattern: dish1 + "1" + dish2 + "0" (winner beats loser)
            pattern = r'(.+?)([01])(.+?)([01])$'
            match = re.match(pattern, line)
            
            if match:
                dish1, score1, dish2, score2 = match.groups()
                score1, score2 = int(score1), int(score2)
                
                if score1 == 1 and score2 == 0:
                    winner, loser = dish1, dish2
                elif score1 == 0 and score2 == 1:
                    winner, loser = dish2, dish1
                else:
                    st.warning(f"Invalid score on line {line_num}: {line}")
                    continue
                
                matches.append((winner, loser))
            else:
                st.warning(f"Could not parse line {line_num}: {line}")
        
        return matches
    
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
        
        old_winner_elo = Ra
        old_loser_elo = Rb
        
        self.elo[winner] = Ra + k * (1 - Ea)
        self.elo[loser] = Rb + k * (0 - Eb)
        
        self.games_played[winner] += 1
        self.games_played[loser] += 1
        
        return old_winner_elo, old_loser_elo
    
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
    
    def create_plotly_chart(self):
        """Create interactive Plotly chart"""
        official_df, provisional_df = self.generate_ranking_report()
        
        fig = go.Figure()
        
        # Add official ranking bars
        if not official_df.empty:
            fig.add_trace(go.Bar(
                y=official_df["Dish"],
                x=official_df["Elo Score"],
                orientation='h',
                name='Official (3+ games)',
                marker_color='orange',
                text=[f"{row['Elo Score']:.0f}" for _, row in official_df.iterrows()],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Elo: %{x:.0f}<br>Games: %{customdata}<extra></extra>',
                customdata=official_df["Games Played"]
            ))
        
        # Add provisional ranking bars
        if not provisional_df.empty:
            fig.add_trace(go.Bar(
                y=provisional_df["Dish"],
                x=provisional_df["Elo Score"],
                orientation='h',
                name='Provisional (<3 games)',
                marker_color='gray',
                text=[f"{row['Elo Score']:.0f}" for _, row in provisional_df.iterrows()],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Elo: %{x:.0f}<br>Games: %{customdata}<extra></extra>',
                customdata=provisional_df["Games Played"]
            ))
        
        # Update layout
        fig.update_layout(
            title="Da Wan Gong Restaurant - Dish Elo Ranking",
            xaxis_title="Elo Score",
            yaxis_title="",
            height=max(400, (len(official_df) + len(provisional_df)) * 40 + 100),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        
        # Reverse y-axis to show highest ranked at top
        fig.update_yaxes(categoryorder="total ascending")
        
        return fig
    
    def save_ratings(self):
        """Save current Elo ratings to file"""
        data = {
            'elo': self.elo,
            'games_played': self.games_played,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.save_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def process_matches(self, content, file_name="New Matches"):
        """Process match content and update rankings"""
        matches = self.parse_match_content(content)
        
        if not matches:
            st.error("No valid matches found in the file!")
            return False
        
        st.success(f"Found {len(matches)} valid matches")
        
        # Process matches
        match_results = []
        for i, (winner, loser) in enumerate(matches, 1):
            old_winner_elo, old_loser_elo = self.update_elo(winner, loser)
            winner_change = self.elo[winner] - old_winner_elo
            loser_change = self.elo[loser] - old_loser_elo
            
            match_results.append({
                'Match': i,
                'Winner': winner,
                'Loser': loser,
                'Winner Elo Change': f"+{winner_change:.1f}",
                'Loser Elo Change': f"{loser_change:.1f}"
            })
        
        # Save ratings
        self.save_ratings()
        
        return match_results

def main():
    st.set_page_config(
        page_title="Restaurant Elo Ranking",
        page_icon="🍽️",
        layout="wide"
    )
    
    # Initialize system
    if 'elo_system' not in st.session_state:
        st.session_state.elo_system = StreamlitEloSystem()
    
    elo_system = st.session_state.elo_system
    
    # Title and description
    st.title("🍽️ Da Wan Gong Restaurant Ranking System")
    st.markdown("Upload txt files with pairwise comparison results to update dish rankings!")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Upload New Matches")
        uploaded_file = st.file_uploader(
            "Choose a txt file",
            type=['txt'],
            help="Upload a file with format: 菜品A1菜品B0"
        )
        
        if uploaded_file is not None:
            # Read file content
            content = uploaded_file.read().decode('utf-8')
            file_name = uploaded_file.name
            
            st.text_area("File Preview:", content[:500] + "..." if len(content) > 500 else content, height=150)
            
            if st.button("🚀 Process Matches", type="primary"):
                with st.spinner("Processing matches..."):
                    match_results = elo_system.process_matches(content, file_name)
                    
                    if match_results:
                        st.success(f"✅ Processed {len(match_results)} matches from {file_name}")
                        
                        # Show match results in sidebar
                        st.subheader("Match Results:")
                        results_df = pd.DataFrame(match_results)
                        st.dataframe(results_df, hide_index=True)
                        
                        # Force refresh of the main content
                        st.rerun()
        
        # Clear all data button
        st.markdown("---")
        if st.button("🗑️ Reset All Data", help="Clear all rankings and start fresh"):
            if os.path.exists(elo_system.save_file):
                os.remove(elo_system.save_file)
            st.session_state.elo_system = StreamlitEloSystem()
            st.success("All data cleared!")
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Current Rankings")
        
        # Generate and display rankings
        official_df, provisional_df = elo_system.generate_ranking_report()
        
        if official_df.empty and provisional_df.empty:
            st.info("No rankings yet. Upload a match file to get started!")
        else:
            # Create and display interactive chart
            fig = elo_system.create_plotly_chart()
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.header("📈 Statistics")
        
        total_dishes = len(elo_system.elo)
        total_games = sum(elo_system.games_played.values())
        official_count = len(official_df)
        provisional_count = len(provisional_df)
        
        # Display stats
        st.metric("Total Dishes", total_dishes)
        st.metric("Total Games", total_games)
        st.metric("Official Ranking", official_count)
        st.metric("Provisional Ranking", provisional_count)
        
        # Show detailed rankings
        if not official_df.empty:
            st.subheader("🏆 Official Ranking")
            for i, (_, row) in enumerate(official_df.iterrows(), 1):
                st.write(f"**#{i}** {row['Dish']} - {row['Elo Score']:.0f} ({row['Games Played']} games)")
        
        if not provisional_df.empty:
            st.subheader("⏳ Provisional Ranking")
            for i, (_, row) in enumerate(provisional_df.iterrows(), 1):
                st.write(f"**#{i}** {row['Dish']} - {row['Elo Score']:.0f} ({row['Games Played']} games)")
        
        # Export data
        if total_dishes > 0:
            st.markdown("---")
            st.subheader("💾 Export Data")
            
            # Create export data
            all_data = []
            for dish, elo_score in elo_system.elo.items():
                all_data.append({
                    'Dish': dish,
                    'Elo Score': round(elo_score, 1),
                    'Games Played': elo_system.games_played[dish],
                    'Status': 'Official' if elo_system.games_played[dish] >= 3 else 'Provisional'
                })
            
            export_df = pd.DataFrame(all_data)
            export_df = export_df.sort_values('Elo Score', ascending=False)
            
            csv = export_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"restaurant_rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )
    
    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit | Restaurant Elo Ranking System")

if __name__ == "__main__":
    main()