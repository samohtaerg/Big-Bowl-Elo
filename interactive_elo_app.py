# -*- coding: utf-8 -*-
"""Interactive Click-based Restaurant Elo Ranking System"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import json
import os
from datetime import datetime
import plotly.graph_objects as go
from itertools import combinations
import random

# Language configurations
LANGUAGES = {
    'zh': {
        'name': '中文',
        'app_title': '大碗公餐厅排行榜',
        'homepage_title': '🏠 大碗公 餐厅排行榜',
        'pk_title': '⚔️ 菜品PK对战模式',
        'navigation': '🧭 导航',
        'homepage': '🏠 主页排名',
        'pk_mode': '⚔️ PK对战',
        'welcome_guide': '📖 使用指南：',
        'guide_step1': '1. 点击左侧 "⚔️ PK对战" 开始菜品比较',
        'guide_step2': '2. 选择想要比较的菜品',
        'guide_step3': '3. 进行一对一PK选择',
        'guide_step4': '4. 排名会自动更新并显示在这里',
        'ranking_rules': '🎯 排名规则：',
        'official_ranking': '**正式排名（橙色）**：参与3场及以上比赛的菜品',
        'provisional_ranking': '**临时排名（灰色）**：参与少于3场比赛的菜品',
        'elo_explanation': '每次PK胜利会增加Elo分数，失败会减少',
        'start_first_pk': '🚀 现在开始你的第一次PK吧！',
        'start_pk_btn': '🚀 开始第一次PK',
        'current_ranking': '📊 当前排名概览',
        'total_dishes': '参与菜品',
        'total_battles': '总对战数',
        'official_count': '正式排名',
        'provisional_count': '临时排名',
        'continue_pk': '🆕 继续PK对战',
        'reset_data': '🔄 重置所有数据',
        'reset_confirm': '⚠️ 确定要清除所有数据吗？此操作无法撤销！',
        'confirm_reset': '✅ 确认重置',
        'cancel': '❌ 取消',
        'data_reset_success': '数据已重置！',
        'ranking_details': '🏅 排名详情',
        'official_ranking_detail': '🥇 正式排名 (3+ 场比赛)',
        'provisional_ranking_detail': '⏳ 临时排名 (<3 场比赛)',
        'select_dishes': '🍽️ 选择参战菜品',
        'select_dishes_desc': '点击选择想要参与PK的菜品（建议3-6个）：',
        'selected_dishes': '已选择的菜品：',
        'battle_count': '将进行',
        'battles': '场PK对战',
        'start_battle': '🚀 开始PK对战！',
        'min_dishes_warning': '请至少选择2个菜品才能开始PK',
        'reselect': '🔄 重新选择',
        'current_ranking_preview': '📊 当前排名预览',
        'no_ranking_data': '还没有排名数据\n开始PK来建立排名吧！',
        'total_dishes_metric': '总菜品数',
        'total_battles_metric': '总对战数',
        'official_top5': '**🏆 正式排名前5:**',
        'provisional_top3': '**⏳ 临时排名:**',
        'battle_progress': '对战进度：',
        'battle_round': '⚔️ 第',
        'round': '场对战',
        'choose_better': '请选择你认为更好吃的菜品：',
        'elo_score': 'Elo分数:',
        'battles_played': '已对战:',
        'games_unit': '场',
        'vs': 'VS',
        'select': '选择',
        'all_battles_complete': '🎉 所有对战完成！',
        'battle_results': '📊 本轮对战结果',
        'battle_vs': '战胜',
        'updated_rankings': '🏆 更新后的排名',
        'continue_battle': '🔄 继续PK对战',
        'back_home': '🏠 返回主页',
        'chart_title': '大碗公餐厅 - 菜品Elo排名',
        'official_3plus': 'Official (3+ games)',
        'provisional_less3': 'Provisional (<3 games)'
    },
    'en': {
        'name': 'English',
        'app_title': 'Big Bowl Noodle House Ranking',
        'homepage_title': '🏠 Big Bowl Noodle House Ranking',
        'pk_title': '⚔️ Dish PK Battle Mode',
        'navigation': '🧭 Navigation',
        'homepage': '🏠 Homepage',
        'pk_mode': '⚔️ PK Battle',
        'welcome_guide': '📖 User Guide:',
        'guide_step1': '1. Click "⚔️ PK Battle" on the left to start dish comparison',
        'guide_step2': '2. Select dishes you want to compare',
        'guide_step3': '3. Make one-on-one PK choices',
        'guide_step4': '4. Rankings will be automatically updated and displayed here',
        'ranking_rules': '🎯 Ranking Rules:',
        'official_ranking': '**Official Ranking (Orange)**: Dishes with 3+ battles',
        'provisional_ranking': '**Provisional Ranking (Gray)**: Dishes with <3 battles',
        'elo_explanation': 'Each PK victory increases Elo score, defeat decreases it',
        'start_first_pk': '🚀 Start your first PK battle now!',
        'start_pk_btn': '🚀 Start First PK',
        'current_ranking': '📊 Current Rankings Overview',
        'total_dishes': 'Total Dishes',
        'total_battles': 'Total Battles',
        'official_count': 'Official Ranking',
        'provisional_count': 'Provisional Ranking',
        'continue_pk': '🆕 Continue PK Battle',
        'reset_data': '🔄 Reset All Data',
        'reset_confirm': '⚠️ Are you sure you want to clear all data? This cannot be undone!',
        'confirm_reset': '✅ Confirm Reset',
        'cancel': '❌ Cancel',
        'data_reset_success': 'Data has been reset!',
        'ranking_details': '🏅 Ranking Details',
        'official_ranking_detail': '🥇 Official Ranking (3+ battles)',
        'provisional_ranking_detail': '⏳ Provisional Ranking (<3 battles)',
        'select_dishes': '🍽️ Select Battle Dishes',
        'select_dishes_desc': 'Click to select dishes for PK battle (recommend 3-6):',
        'selected_dishes': 'Selected Dishes:',
        'battle_count': 'Will have',
        'battles': 'PK battles',
        'start_battle': '🚀 Start PK Battle!',
        'min_dishes_warning': 'Please select at least 2 dishes to start PK',
        'reselect': '🔄 Reselect',
        'current_ranking_preview': '📊 Current Ranking Preview',
        'no_ranking_data': 'No ranking data yet\nStart PK to build rankings!',
        'total_dishes_metric': 'Total Dishes',
        'total_battles_metric': 'Total Battles',
        'official_top5': '**🏆 Official Top 5:**',
        'provisional_top3': '**⏳ Provisional:**',
        'battle_progress': 'Battle Progress:',
        'battle_round': '⚔️ Battle',
        'round': '',
        'choose_better': 'Please choose the dish you think tastes better:',
        'elo_score': 'Elo Score:',
        'battles_played': 'Battles:',
        'games_unit': '',
        'vs': 'VS',
        'select': 'Choose',
        'all_battles_complete': '🎉 All Battles Complete!',
        'battle_results': '📊 Battle Results This Round',
        'battle_vs': 'defeated',
        'updated_rankings': '🏆 Updated Rankings',
        'continue_battle': '🔄 Continue PK Battle',
        'back_home': '🏠 Back to Home',
        'chart_title': 'Da Wan Gong Restaurant - Dish Elo Ranking',
        'official_3plus': 'Official (3+ games)',
        'provisional_less3': 'Provisional (<3 games)'
    }
}

def get_text(key, lang='zh'):
    """Get text based on current language"""
    return LANGUAGES.get(lang, LANGUAGES['zh']).get(key, key)

# Set Chinese font for matplotlib
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class InteractiveEloSystem:
    def __init__(self, save_file="elo_ratings.json", menu_file="menu_names.txt"):
        self.save_file = save_file
        self.menu_file = menu_file
        self.load_menu()
        self.load_existing_ratings()
    
    def load_menu(self):
        """Load menu from text file"""
        self.all_dishes = []
        encodings_to_try = ['utf-8-sig', 'utf-8', 'gb2312', 'gbk', 'cp936']
        
        if not os.path.exists(self.menu_file):
            # Default menu if file doesn't exist
            self.all_dishes = [
                "独家大碗米粉", "猪骨汤米线", "番茄汤米线", "沙爹米线", "泡椒酸米线",
                "椒麻鸡丁饭", "咖喱鱼丸", "西兰花牛肉饭", "鱼香烘蛋饭", "星洲炒米粉",
                "叉烧炒饭", "皮蛋瘦肉粥", "滑蛋叉烧饭", "红烧牛肉面", "麻辣牛腩牛腱牛百叶汤米线"
            ]
            return
        
        for encoding in encodings_to_try:
            try:
                with open(self.menu_file, 'r', encoding=encoding) as f:
                    self.all_dishes = []
                    for line in f:
                        line = line.strip()
                        if line:  # Skip empty lines
                            # Check if line has format "数字→菜名" or just "菜名"
                            if '→' in line:
                                dish_name = line.split('→')[1].strip()
                            else:
                                dish_name = line
                            
                            if dish_name:
                                self.all_dishes.append(dish_name)
                if len(self.all_dishes) > 0:
                    break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if not self.all_dishes:
            # Fallback menu
            self.all_dishes = [
                "独家大碗米粉", "猪骨汤米线", "番茄汤米线", "沙爹米线", "泡椒酸米线",
                "椒麻鸡丁饭", "咖喱鱼丸", "西兰花牛肉饭", "鱼香烘蛋饭", "星洲炒米粉",
                "叉烧炒饭", "皮蛋瘦肉粥", "滑蛋叉烧饭", "红烧牛肉面", "麻辣牛腩牛腱牛百叶汤米线"
            ]
    
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
    
    def create_plotly_chart(self, lang='zh'):
        """Create interactive Plotly chart"""
        official_df, provisional_df = self.generate_ranking_report()
        
        fig = go.Figure()
        
        # Add official ranking bars
        if not official_df.empty:
            fig.add_trace(go.Bar(
                y=official_df["Dish"],
                x=official_df["Elo Score"],
                orientation='h',
                name=get_text('official_3plus', lang),
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
                name=get_text('provisional_less3', lang),
                marker_color='gray',
                text=[f"{row['Elo Score']:.0f}" for _, row in provisional_df.iterrows()],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Elo: %{x:.0f}<br>Games: %{customdata}<extra></extra>',
                customdata=provisional_df["Games Played"]
            ))
        
        # Update layout
        fig.update_layout(
            title=get_text('chart_title', lang),
            xaxis_title="Elo Score",
            yaxis_title="",
            height=max(400, (len(official_df) + len(provisional_df)) * 40 + 100),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.6,  # Move legend much further down
                xanchor="center",
                x=0.5
            ),
            margin=dict(b=120)  # Increase bottom margin for legend
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

def main():
    st.set_page_config(
        page_title="Da Wan Gong Restaurant Ranking",
        page_icon="🍽️",
        layout="wide"
    )
    
    # Initialize language
    if 'language' not in st.session_state:
        st.session_state.language = 'zh'
    
    # Language switcher in the top right
    col1, col2 = st.columns([4, 1])
    with col2:
        lang_options = ['zh', 'en']
        lang_labels = [LANGUAGES[lang]['name'] for lang in lang_options]
        current_index = lang_options.index(st.session_state.language)
        
        selected_lang = st.selectbox(
            "🌐", 
            lang_options, 
            format_func=lambda x: LANGUAGES[x]['name'],
            index=current_index,
            key="language_selector"
        )
        
        if selected_lang != st.session_state.language:
            st.session_state.language = selected_lang
            st.rerun()
    
    lang = st.session_state.language
    
    # Initialize system
    if 'elo_system' not in st.session_state:
        st.session_state.elo_system = InteractiveEloSystem()
    if 'selected_dishes' not in st.session_state:
        st.session_state.selected_dishes = []
    if 'current_battles' not in st.session_state:
        st.session_state.current_battles = []
    if 'current_battle_index' not in st.session_state:
        st.session_state.current_battle_index = 0
    if 'battle_results' not in st.session_state:
        st.session_state.battle_results = []
    if 'battle_mode' not in st.session_state:
        st.session_state.battle_mode = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "homepage"
    
    elo_system = st.session_state.elo_system
    
    # Navigation
    st.sidebar.title(get_text('navigation', lang))
    page_options = {
        "homepage": get_text('homepage', lang),
        "pk_mode": get_text('pk_mode', lang)
    }
    
    selected_page = st.sidebar.radio(
        "", 
        list(page_options.keys()), 
        format_func=lambda x: page_options[x],
        index=0 if st.session_state.current_page == "homepage" else 1
    )
    
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        if selected_page != "pk_mode":
            st.session_state.battle_mode = False
        st.rerun()
    
    # Homepage
    if st.session_state.current_page == "homepage":
        show_homepage(elo_system, lang)
    
    # PK Mode
    elif st.session_state.current_page == "pk_mode":
        show_pk_mode(elo_system, lang)

def show_homepage(elo_system, lang='zh'):
    """Display homepage with current rankings"""
    st.title(get_text('homepage_title', lang))
    
    # Welcome message
    official_df, provisional_df = elo_system.generate_ranking_report()
    total_dishes = len(elo_system.elo)
    total_games = sum(elo_system.games_played.values())
    
    if total_dishes == 0:
        welcome_msg = f"""
        ## 🌟 {get_text('welcome_guide', lang).replace('📖 ', '')}
        
        ### {get_text('welcome_guide', lang)}
        {get_text('guide_step1', lang)}
        {get_text('guide_step2', lang)}
        {get_text('guide_step3', lang)}
        {get_text('guide_step4', lang)}
        
        ### {get_text('ranking_rules', lang)}
        - {get_text('official_ranking', lang)}
        - {get_text('provisional_ranking', lang)}
        - {get_text('elo_explanation', lang)}
        
        ### {get_text('start_first_pk', lang)}
        """
        st.markdown(welcome_msg)
        
        # Quick start button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(get_text('start_pk_btn', lang), type="primary"):
                st.session_state.current_page = "pk_mode"
                st.rerun()
    else:
        # Show current rankings
        st.markdown(f"""
        ## {get_text('current_ranking', lang)}
        
        **{get_text('current_ranking', lang).replace('📊 ', '')}:**
        - 🍽️ {get_text('total_dishes', lang)}：{total_dishes} {'道' if lang == 'zh' else ''}
        - ⚔️ {get_text('total_battles', lang)}：{total_games} {'场' if lang == 'zh' else ''}
        - 🏆 {get_text('official_count', lang)}：{len(official_df)} {'道菜' if lang == 'zh' else ' dishes'}
        - ⏳ {get_text('provisional_count', lang)}：{len(provisional_df)} {'道菜' if lang == 'zh' else ' dishes'}
        """)
        
        # Main ranking chart with mobile scroll support
        fig = elo_system.create_plotly_chart(lang)
        
        # Add container with horizontal scroll for mobile
        st.markdown("""
        <style>
        .plotly-chart-container {
            overflow-x: auto;
            min-width: 100%;
        }
        @media (max-width: 768px) {
            .plotly-chart-container {
                overflow-x: scroll;
                -webkit-overflow-scrolling: touch;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.plotly_chart(fig, use_container_width=True)
        
        # Quick actions
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button(get_text('continue_pk', lang), type="primary"):
                st.session_state.current_page = "pk_mode"
                st.rerun()
        
        with col2:
            # Add confirmation state for reset
            if 'confirm_reset' not in st.session_state:
                st.session_state.confirm_reset = False
                
            if not st.session_state.confirm_reset:
                if st.button(get_text('reset_data', lang), type="secondary"):
                    st.session_state.confirm_reset = True
                    st.rerun()
            else:
                st.warning(get_text('reset_confirm', lang))
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(get_text('confirm_reset', lang), type="primary"):
                        if os.path.exists(elo_system.save_file):
                            os.remove(elo_system.save_file)
                        st.session_state.elo_system = InteractiveEloSystem()
                        st.session_state.confirm_reset = False
                        st.success(get_text('data_reset_success', lang))
                        st.rerun()
                with col_b:
                    if st.button(get_text('cancel', lang), type="secondary"):
                        st.session_state.confirm_reset = False
                        st.rerun()
        
        # Recent activity
        if not official_df.empty or not provisional_df.empty:
            st.markdown(f"### {get_text('ranking_details', lang)}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if not official_df.empty:
                    st.markdown(f"#### {get_text('official_ranking_detail', lang)}")
                    for i, (_, row) in enumerate(official_df.head(10).iterrows(), 1):
                        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
                        score_text = f"{row['Elo Score']:.0f}{'分' if lang == 'zh' else ''}"
                        games_text = f"({row['Games Played']}{'场' if lang == 'zh' else ' games'})"
                        st.write(f"{medal} **{row['Dish']}** - {score_text} {games_text}")
            
            with col2:
                if not provisional_df.empty:
                    st.markdown(f"#### {get_text('provisional_ranking_detail', lang)}")
                    for i, (_, row) in enumerate(provisional_df.head(10).iterrows(), 1):
                        score_text = f"{row['Elo Score']:.0f}{'分' if lang == 'zh' else ''}"
                        games_text = f"({row['Games Played']}{'场' if lang == 'zh' else ' games'})"
                        st.write(f"#{i} **{row['Dish']}** - {score_text} {games_text}")

def show_pk_mode(elo_system, lang='zh'):
    """Display PK battle mode"""
    st.title(get_text('pk_title', lang))
    
    # Main PK interface
    if not st.session_state.battle_mode:
        # Dish selection mode
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("🍽️ 选择参战菜品")
            st.markdown("点击选择想要参与PK的菜品（建议3-6个）：")
            
            # Create columns for dish selection
            cols = st.columns(4)
            
            for i, dish in enumerate(elo_system.all_dishes):
                col_idx = i % 4
                with cols[col_idx]:
                    # Get current Elo for display
                    current_elo = elo_system.elo.get(dish, 1500)
                    games_count = elo_system.games_played.get(dish, 0)
                    
                    # Create checkbox for selection
                    is_selected = dish in st.session_state.selected_dishes
                    selected = st.checkbox(
                        f"**{dish}**\n{current_elo:.0f}分 ({games_count}场)",
                        value=is_selected,
                        key=f"dish_{i}"
                    )
                    
                    # Update selection
                    if selected and dish not in st.session_state.selected_dishes:
                        st.session_state.selected_dishes.append(dish)
                    elif not selected and dish in st.session_state.selected_dishes:
                        st.session_state.selected_dishes.remove(dish)
            
            # Selected dishes display
            if st.session_state.selected_dishes:
                st.markdown("---")
                st.subheader("已选择的菜品：")
                selected_text = " | ".join(st.session_state.selected_dishes)
                st.success(f"🥘 {selected_text}")
                
                battle_count = len(list(combinations(st.session_state.selected_dishes, 2)))
                st.info(f"将进行 **{battle_count}** 场PK对战")
                
                # Start battle button
                if len(st.session_state.selected_dishes) >= 2:
                    if st.button("🚀 开始PK对战！", type="primary"):
                        # Generate all battle pairs
                        st.session_state.current_battles = list(combinations(st.session_state.selected_dishes, 2))
                        # Shuffle for randomness
                        random.shuffle(st.session_state.current_battles)
                        st.session_state.current_battle_index = 0
                        st.session_state.battle_results = []
                        st.session_state.battle_mode = True
                        st.rerun()
                else:
                    st.warning("请至少选择2个菜品才能开始PK")
            
            # Clear selection button
            if st.session_state.selected_dishes:
                if st.button("🔄 重新选择", type="secondary"):
                    st.session_state.selected_dishes = []
                    st.rerun()
        
        with col2:
            st.header("📊 当前排名预览")
            
            # Generate and display rankings
            official_df, provisional_df = elo_system.generate_ranking_report()
            
            if official_df.empty and provisional_df.empty:
                st.info("还没有排名数据\n开始PK来建立排名吧！")
            else:
                # Statistics
                total_dishes = len(elo_system.elo)
                total_games = sum(elo_system.games_played.values())
                st.metric("总菜品数", total_dishes)
                st.metric("总对战数", total_games)
                
                # Top dishes preview
                if not official_df.empty:
                    st.markdown("**🏆 正式排名前5:**")
                    for i, (_, row) in enumerate(official_df.head(5).iterrows(), 1):
                        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
                        st.write(f"{emoji} {row['Dish']} - {row['Elo Score']:.0f}分")
                
                if not provisional_df.empty:
                    st.markdown("**⏳ 临时排名:**")
                    for i, (_, row) in enumerate(provisional_df.head(3).iterrows(), 1):
                        st.write(f"#{i} {row['Dish']} - {row['Elo Score']:.0f}分")

    else:
        # Battle mode
        current_index = st.session_state.current_battle_index
        total_battles = len(st.session_state.current_battles)
        
        if current_index < total_battles:
            # Current battle
            dish1, dish2 = st.session_state.current_battles[current_index]
            
            # Progress bar
            progress = (current_index) / total_battles
            st.progress(progress, text=f"对战进度：{current_index}/{total_battles}")
            
            st.header(f"⚔️ 第 {current_index + 1} 场对战")
            st.markdown("### 请选择你认为更好吃的菜品：")
            
            # Battle interface
            col1, col2, col3 = st.columns([1, 0.3, 1])
            
            with col1:
                # Get current stats
                elo1 = elo_system.elo.get(dish1, 1500)
                games1 = elo_system.games_played.get(dish1, 0)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; border: 2px solid #ff6b6b; border-radius: 10px; background-color: #ffe6e6;">
                    <h3 style="color: #d32f2f;">{dish1}</h3>
                    <p><strong>Elo分数:</strong> {elo1:.0f}</p>
                    <p><strong>已对战:</strong> {games1}场</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"选择 {dish1}", type="primary", key="choice1"):
                    # Record result
                    old_elo1, old_elo2 = elo_system.update_elo(dish1, dish2)
                    
                    st.session_state.battle_results.append({
                        'winner': dish1,
                        'loser': dish2,
                        'winner_change': elo_system.elo[dish1] - old_elo1,
                        'loser_change': elo_system.elo[dish2] - old_elo2
                    })
                    
                    st.session_state.current_battle_index += 1
                    elo_system.save_ratings()
                    st.rerun()
            
            with col2:
                st.markdown("<div style='text-align: center; padding: 30px;'><h2>VS</h2></div>", unsafe_allow_html=True)
            
            with col3:
                # Get current stats
                elo2 = elo_system.elo.get(dish2, 1500)
                games2 = elo_system.games_played.get(dish2, 0)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; border: 2px solid #4caf50; border-radius: 10px; background-color: #e8f5e8;">
                    <h3 style="color: #2e7d32;">{dish2}</h3>
                    <p><strong>Elo分数:</strong> {elo2:.0f}</p>
                    <p><strong>已对战:</strong> {games2}场</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"选择 {dish2}", type="primary", key="choice2"):
                    # Record result
                    old_elo1, old_elo2 = elo_system.update_elo(dish2, dish1)
                    
                    st.session_state.battle_results.append({
                        'winner': dish2,
                        'loser': dish1,
                        'winner_change': elo_system.elo[dish2] - old_elo2,
                        'loser_change': elo_system.elo[dish1] - old_elo1
                    })
                    
                    st.session_state.current_battle_index += 1
                    elo_system.save_ratings()
                    st.rerun()
        
        else:
            # Battle completed
            st.header("🎉 所有对战完成！")
            st.balloons()
            
            # Show results summary
            if st.session_state.battle_results:
                st.subheader("📊 本轮对战结果")
                results_df = pd.DataFrame(st.session_state.battle_results)
                
                for i, result in enumerate(st.session_state.battle_results, 1):
                    st.write(f"**第{i}场:** {result['winner']} 战胜 {result['loser']} "
                           f"(+{result['winner_change']:.1f} / {result['loser_change']:.1f})")
            
            # Show updated rankings with mobile scroll support
            st.subheader("🏆 更新后的排名")
            fig = elo_system.create_plotly_chart()
            
            # Add container with horizontal scroll for mobile
            st.markdown("""
            <style>
            .plotly-chart-container {
                overflow-x: auto;
                min-width: 100%;
            }
            @media (max-width: 768px) {
                .plotly-chart-container {
                    overflow-x: scroll;
                    -webkit-overflow-scrolling: touch;
                }
            }
            </style>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.plotly_chart(fig, use_container_width=True)
            
            # Buttons to continue or reset
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 继续PK对战", type="primary"):
                    st.session_state.battle_mode = False
                    st.session_state.selected_dishes = []
                    st.session_state.current_battles = []
                    st.session_state.current_battle_index = 0
                    st.session_state.battle_results = []
                    st.rerun()
            
            with col2:
                if st.button("🏠 返回主页", type="secondary"):
                    st.session_state.current_page = "homepage"
                    st.session_state.battle_mode = False
                    st.session_state.selected_dishes = []
                    st.session_state.current_battles = []
                    st.session_state.current_battle_index = 0
                    st.session_state.battle_results = []
                    st.rerun()


if __name__ == "__main__":
    main()
