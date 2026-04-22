import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
#loading
@st.cache_data
def load_universities_data():
    return pd.read_csv('data/universities.csv')
@st.cache_data
def load_olympiad_bonuses():
    return pd.read_csv('data/olympiad_bonuses.csv')
@st.cache_data
def load_achievement_bonuses():
    return pd.read_csv('data/achievement_bonuses.csv')
universities_df = load_universities_data()
olympiad_bonuses_df = load_olympiad_bonuses()
achievement_bonuses_df = load_achievement_bonuses()
OLYMPIAD_BONUSES = dict(zip(olympiad_bonuses_df['olympiad_level'], 
                            olympiad_bonuses_df['bonus_points']))

ACHIEVEMENT_BONUSES = dict(zip(achievement_bonuses_df['achievement'], 
                               achievement_bonuses_df['bonus_points']))
#functions
def calculate_total_score(math, russian, informatics, gpa, olympiad_level, achievements):
    ege_sum = math + russian + informatics
    if gpa >= 4.8:
        gpa_bonus = 5
    elif gpa >= 4.5:
        gpa_bonus = 3
    elif gpa >= 4.0:
        gpa_bonus = 1
    else:
        gpa_bonus = 0
    olympiad_bonus = OLYMPIAD_BONUSES.get(olympiad_level, 0)
    achievements_bonus = 0
    if achievements.get("gold_gto"):
        achievements_bonus += ACHIEVEMENT_BONUSES.get("gold_gto", 0)
    if achievements.get("volunteer_hours", 0) >= 100:
        achievements_bonus += ACHIEVEMENT_BONUSES.get("volunteer_100", 0)
    elif achievements.get("volunteer_hours", 0) >= 50:
        achievements_bonus += ACHIEVEMENT_BONUSES.get("volunteer_50", 0)
    if achievements.get("final_essay"):
        achievements_bonus += ACHIEVEMENT_BONUSES.get("final_essay", 0)
    if achievements.get("gold_medal"):
        achievements_bonus += ACHIEVEMENT_BONUSES.get("gold_medal", 0)
    elif achievements.get("silver_medal"):
        achievements_bonus += ACHIEVEMENT_BONUSES.get("silver_medal", 0)
    total = ege_sum + gpa_bonus + olympiad_bonus + achievements_bonus
    return total, {
        "ege_sum": ege_sum,
        "gpa_bonus": gpa_bonus,
        "olympiad_bonus": olympiad_bonus,
        "achievements_bonus": achievements_bonus
    }
# Загрузка CSS
def load_css():
    css_path = os.path.join('styles', 'custom.css')
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass
load_css()
#probability
def calculate_probability(student_score, passing_score, competition):
    if student_score >= passing_score:
        base = 0.7 + 2 * (student_score - passing_score) / passing_score
        base = min(base, 0.98)
    else:
        base = 0.7 + 2.5 * (student_score - passing_score) / passing_score
        base = max(base, 0.05)
    if competition > 3:
        competition_factor = 9.0 / competition
    else:
        competition_factor = 1.0
    probability = base * competition_factor * 100
    return round(probability, 1)
def get_region_options():
    return universities_df['region'].unique().tolist()
def get_universities_by_region(region):
    return universities_df[universities_df['region'] == region]['university'].unique().tolist()
def get_programs_by_university(region, university):
    df_filtered = universities_df[
        (universities_df['region'] == region) & 
        (universities_df['university'] == university)
    ]
    return df_filtered['program'].unique().tolist()
def get_university_data(region, university, program):
    df_filtered = universities_df[
        (universities_df['region'] == region) &
        (universities_df['university'] == university) &
        (universities_df['program'] == program)
    ]
    if len(df_filtered) > 0:
        row = df_filtered.iloc[0]
        return {
            "passing": row['passing_score'],
            "competition": row['competition'],
            "budget_places": row['budget_places']
        }
    return None
def create_comparison_chart(student_score, passing_score, university, program):
    fig, ax = plt.subplots(figsize=(8, 3))
    categories = [f"{university}\n{program}", "Проходной балл"]
    values = [student_score, passing_score]
    colors = ["#4CAF50" if student_score >= passing_score else "#FF9800", "#2196F3"]
    ax.bar(categories, values, color=colors, alpha=0.8)
    ax.set_ylabel("Баллы")
    ax.set_title("Сравнение ваших баллов с проходным баллом")
    ax.axhline(y=passing_score, color="red", linestyle="--", alpha=0.5, label="Порог")
    ax.legend()
    plt.tight_layout()
    return fig
def find_alternatives(student_score, current_university, current_program, region_filter=None):
    alternatives = []
    df = universities_df
    if region_filter:
        df = df[df['region'] == region_filter]
    for _, row in df.iterrows():
        if row['university'] == current_university and row['program'] == current_program:
            continue
        passing = row['passing_score']
        if student_score >= passing:
            status = "✅ Хорошие шансы"
        elif student_score >= passing - 20:
            status = "⚠️Погранично"
        else:
            status = "‼️ Низкие шансы"
        alternatives.append({
            "university": row['university'],
            "program": row['program'],
            "passing": passing,
            "difference": student_score - passing,
            "status": status
        }) 
    alternatives.sort(key=lambda x: x["difference"], reverse=True)
    return alternatives[:5]
#interface
st.markdown("""
<style>
/* Скрываем обе иконки Material Icons */
[data-testid="stIconMaterial"] {
    display: none !important;
}

/* Добавляем свою стрелку на кнопку */
[data-testid="stSidebarCollapseButton"] button {
    position: relative;
}

/* Стрелка когда панель ОТКРЫТА (было keyboard_double_arrow_left) */
[data-testid="stSidebarCollapseButton"] button::before {
    content: "◀";
    font-size: 14px;
    color: #666;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
}

/* Стрелка когда панель СВЁРНУТА (было keyboard_double_arrow_right) */
[data-testid="stSidebarCollapsed"] [data-testid="stSidebarCollapseButton"] button::before {
    content: "▶";
}
</style>
""", unsafe_allow_html=True)
st.set_page_config(page_title="Помощник в поступлении", page_icon="📋", layout="wide")
st.title("📋Помощник в поступлении")
st.markdown("---")
with st.sidebar:
    st.header("Данные абитуриента✏️")
    st.subheader("Результаты ЕГЭ")
    math_score = st.number_input("Математика (профиль)", 0, 100, 82)
    russian_score = st.number_input("Русский язык", 0, 100, 91)
    informatics_score = st.number_input("Информатика / Физика", 0, 100, 78)
    st.subheader("Школьные достижения")
    gpa = st.number_input("Средний балл аттестата", 0.0, 5.0, 4.6, step=0.05)
    olympiad = st.selectbox(
        "Олимпиады",
        ["Нет", "Региональный этап", "Перечневая (1-2 уровень)", "Всероссийский этап"]
    )
    with st.expander("Индивидуальные достижения"):
        gold_gto = st.checkbox("Золотой значок ГТО")
        volunteer_hours = st.selectbox("Волонтерские часы", [0, 50, 100, 150, 200])
        final_essay = st.checkbox("Итоговое сочинение (зачет)")
        gold_medal = st.checkbox("Золотая медаль🥇")
        silver_medal = st.checkbox("Серебряная медаль🥈")  
    achievements = {
        "gold_gto": gold_gto,
        "volunteer_hours": volunteer_hours,
        "final_essay": final_essay,
        "gold_medal": gold_medal,
        "silver_medal": silver_medal
    } 
    st.markdown("---")
    st.header("🎓Выбор вуза")
    regions = get_region_options()
    selected_region = st.selectbox("Регион", regions)
    universities = get_universities_by_region(selected_region)
    selected_university = st.selectbox("Вуз", universities)
    programs = get_programs_by_university(selected_region, selected_university)
    selected_program = st.selectbox("Направление", programs)    
    st.markdown("---")
    st.caption("Данные основаны на проходных баллах 2025 года")
if selected_program:
    uni_data = get_university_data(selected_region, selected_university, selected_program)
    if uni_data:
        passing_score = uni_data["passing"]
        competition = uni_data["competition"]
        budget_places = uni_data["budget_places"]
        total_score, bonuses_detail = calculate_total_score(
            math_score, russian_score, informatics_score, gpa, olympiad, achievements
        )
        probability = calculate_probability(total_score, passing_score, competition)
        st.header("Результат прогнозирования")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Общая сумма результатов ЕГЭ", bonuses_detail["ege_sum"])
        with col2:
            st.metric("Доп. баллы", bonuses_detail["gpa_bonus"] + bonuses_detail["olympiad_bonus"] + bonuses_detail["achievements_bonus"])
        with col3:
            st.metric("Итоговый балл", total_score)
        with col4:
            st.metric("Проходной балл (2025)", passing_score, delta=f"{total_score - passing_score:+d}")
        st.markdown("---")
        st.subheader(f"🎯 Вероятность поступления: {probability}%")
        st.progress(probability / 100)
        if probability >= 70:
            st.success("✅**Высокая вероятность!** Смело подавайте документы в этот вуз.")
        elif probability >= 40:
            st.warning("✔️**Средняя вероятность.** Рекомендуем также рассмотреть альтернативы.")
        else:
            st.error("❌**Низкая вероятность.** Стоит серьезно поработать над баллами или выбрать другой вуз.")
        st.caption(f"Конкурс: {competition} человек на место | Бюджетных мест: {budget_places}")
        st.markdown("---")
        st.subheader("Визуализация")
        fig = create_comparison_chart(total_score, passing_score, selected_university, selected_program)
        st.pyplot(fig)
        st.markdown("---")
        st.subheader("Альтернативные варианты")
        alternatives = find_alternatives(total_score, selected_university, selected_program, selected_region)
        if alternatives:
            alt_data = []
            for alt in alternatives[:5]:
                alt_data.append({
                    "Вуз": alt["university"],
                    "Направление": alt["program"],
                    "Проходной балл": alt["passing"],
                    "Разница": f"{alt['difference']:+d}",
                    "Прогноз": alt["status"]
                })
            alt_df = pd.DataFrame(alt_data)
            st.dataframe(alt_df, width='stretch', hide_index=True)
        else:
            st.info("Альтернативные варианты не найдены. Возможно, стоит рассмотреть другие регионы.")
        with st.expander("🔍 Детализация начисленных баллов"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**ЕГЭ:**")
                st.write(f"- Математика: {math_score}")
                st.write(f"- Русский язык: {russian_score}")
                st.write(f"- Информатика: {informatics_score}")
                st.write(f"**Итого ЕГЭ:** {bonuses_detail['ege_sum']}")
            with col_b:
                st.markdown("**Дополнительные баллы:**")
                st.write(f"- Аттестат (GPA {gpa}): +{bonuses_detail['gpa_bonus']}")
                st.write(f"- Олимпиады ({olympiad}): +{bonuses_detail['olympiad_bonus']}")
                st.write(f"- Индивидуальные достижения: +{bonuses_detail['achievements_bonus']}")
                st.write(f"**Всего доп. баллов:** {bonuses_detail['gpa_bonus'] + bonuses_detail['olympiad_bonus'] + bonuses_detail['achievements_bonus']}")
        st.markdown("---")
        st.caption(f"Прогноз сгенерирован {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        st.caption("Данные носят ознакомительный характер. Окончательное решение остается за приемной комиссией вуза")
else:
    st.info("Выберите вуз и направление в боковой панели, чтобы начать")
