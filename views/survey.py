"""
설문 참여 페이지 (로그인 후)
 - Tab 1 "설문 응시"        : AI의 교육적 효과 인식 10문항(5단 척도)에 응답 → survey_table 저장
 - Tab 2 "설문 결과 시각화" : 전체 요약, 문항별 응답 분포, 문항별 평균, 문항 상세, 통계표
차트는 Streamlit에 함께 설치되는 Altair를 사용합니다. (추가 설치 없음)
"""
import altair as alt
import pandas as pd
import streamlit as st

import db
from survey_items import QCOLS, QUESTIONS, SCALE, SCALE_COLORS, SURVEY_TITLE

TAB_TAKE = "📝 설문 응시"
TAB_RESULT = "📊 설문 결과 시각화"
TAB_KEY = "survey_tab"

LEVELS = list(SCALE.keys())                 # [1, 2, 3, 4, 5]
LEVEL_LABELS = list(SCALE.values())         # ["전혀 아니다", ...]
PINE, MINT = "#0F3D3E", "#3FB39A"
INK, MUTED, GRID = "#16222A", "#6B7A80", "#E1E6E4"
FONT = "Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', sans-serif"


# ====================================================================== 공통
def _tabs():
    """최신 Streamlit은 선택한 탭을 기억(key)하고, 이전 버전은 기본 탭으로 동작합니다."""
    if st.session_state.pop("_goto_results", False):
        st.session_state[TAB_KEY] = TAB_RESULT
    try:
        return st.tabs([TAB_TAKE, TAB_RESULT], key=TAB_KEY, on_change="rerun")
    except TypeError:
        return st.tabs([TAB_TAKE, TAB_RESULT])


def _qlabel(i: int, area: str) -> str:
    return f"Q{i}. {area}"


def render():
    st.title("설문 참여")
    st.caption(f"{SURVEY_TITLE}  |  10문항, 5단 척도 (전혀 아니다 ~ 매우 그렇다)")
    tab_take, tab_result = _tabs()
    with tab_take:
        render_take()
    with tab_result:
        render_result()


# ====================================================================== Tab 1 설문 응시
def render_take():
    user = st.session_state.user
    mine = db.get_my_survey(user["userid"])

    if mine:
        st.info(
            f"{user['username']}님은 {mine['created_at']}에 응답하셨습니다. "
            "답을 바꾸고 다시 제출하면 기존 응답이 새 응답으로 바뀝니다."
        )
    else:
        st.write("각 문항을 읽고 자신의 생각과 가장 가까운 보기를 하나씩 골라 주세요.")

    with st.form("survey_form"):
        answers = {}
        for i, (col, area, text) in enumerate(QUESTIONS, start=1):
            prev = mine[col] if mine else None
            answers[col] = st.radio(
                f"**{i}. {text}**",
                options=LEVELS,
                index=LEVELS.index(prev) if prev in LEVELS else None,
                format_func=lambda v: SCALE[v],
                horizontal=True,
                key=f"ans_{col}",
            )
            if i < len(QUESTIONS):
                st.divider()
        submitted = st.form_submit_button(
            "응답 수정하기" if mine else "설문 제출하기", width="stretch"
        )

    if submitted:
        missing = [str(i) for i, q in enumerate(QCOLS, start=1) if answers[q] is None]
        if missing:
            st.error(f"{', '.join(missing)}번 문항에 응답하지 않았습니다. 모든 문항에 응답해 주세요.")
            return
        ts = db.save_survey(user["userid"], answers)
        st.session_state.flash = (
            "success",
            f"설문이 {'수정' if mine else '제출'}되었습니다. ({ts}) 결과를 확인해 보세요.",
        )
        st.session_state["_goto_results"] = True
        st.rerun()


# ====================================================================== 통계 계산
def compute_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, (col, area, text) in enumerate(QUESTIONS, start=1):
        s = df[col].dropna().astype(int)
        n = len(s)
        counts = s.value_counts().reindex(LEVELS, fill_value=0)
        row = {
            "번호": f"Q{i}",
            "영역": area,
            "문항": text,
            "응답수": n,
            "평균": round(s.mean(), 2) if n else None,
            "표준편차": round(s.std(ddof=1), 2) if n > 1 else None,
            "중앙값": float(s.median()) if n else None,
        }
        for lv in LEVELS:
            row[SCALE[lv]] = int(counts[lv])
        row["긍정 비율(%)"] = round((counts[4] + counts[5]) / n * 100, 1) if n else 0.0
        row["부정 비율(%)"] = round((counts[1] + counts[2]) / n * 100, 1) if n else 0.0
        rows.append(row)
    return pd.DataFrame(rows)


def likert_segments(stats: pd.DataFrame) -> pd.DataFrame:
    """diverging 막대용 구간 계산: '보통이다'를 0 기준선에 반씩 걸치게 배치"""
    segs = []
    for i, r in stats.iterrows():
        n = r["응답수"]
        pct = {lv: (r[SCALE[lv]] / n * 100 if n else 0) for lv in LEVELS}
        start = -(pct[1] + pct[2] + pct[3] / 2)
        for lv in LEVELS:
            segs.append({
                "문항": _qlabel(i + 1, r["영역"]),
                "문항 내용": r["문항"],
                "응답": SCALE[lv],
                "점수": lv,
                "응답수": int(r[SCALE[lv]]),
                "비율": round(pct[lv], 1),
                "x0": start,
                "x1": start + pct[lv],
                "mid": start + pct[lv] / 2,
            })
            start += pct[lv]
    return pd.DataFrame(segs)


# ====================================================================== 차트
def _base_config(chart):
    return (
        chart.configure_view(stroke=None)
        .configure_axis(labelColor=MUTED, titleColor=MUTED, gridColor=GRID,
                        domainColor="#C9D3D0", tickColor="#C9D3D0",
                        labelFont=FONT, titleFont=FONT, labelFontSize=12)
        .configure_legend(labelColor=INK, titleColor=MUTED, labelFont=FONT,
                          titleFont=FONT, labelFontSize=12)
        .configure_text(font=FONT)
    )


def chart_likert(stats: pd.DataFrame):
    seg = likert_segments(stats)
    order = [_qlabel(i, q[1]) for i, q in enumerate(QUESTIONS, start=1)]
    y = alt.Y("문항:N", sort=order, title=None, axis=alt.Axis(labelLimit=160, ticks=False, domain=False))
    color = alt.Color(
        "응답:N",
        scale=alt.Scale(domain=LEVEL_LABELS, range=SCALE_COLORS),
        legend=alt.Legend(title=None, orient="top", direction="horizontal", symbolType="square"),
        sort=LEVEL_LABELS,
    )
    tooltip = [
        alt.Tooltip("문항:N"), alt.Tooltip("문항 내용:N"), alt.Tooltip("응답:N"),
        alt.Tooltip("응답수:Q", title="응답 수"), alt.Tooltip("비율:Q", title="비율(%)", format=".1f"),
    ]
    bars = alt.Chart(seg).mark_bar(height=22, stroke="white", strokeWidth=2).encode(
        x=alt.X("x0:Q", title="← 부정  |  긍정 → (응답 비율 %)",
                scale=alt.Scale(domain=[-100, 100]),
                axis=alt.Axis(values=[-100, -50, 0, 50, 100], labelExpr="abs(datum.value) + '%'")),
        x2="x1:Q", y=y, color=color, order=alt.Order("점수:Q"), tooltip=tooltip,
    )
    # 넓은 구간에만 비율 표시 (모든 칸에 숫자를 쓰지 않음)
    labels = alt.Chart(seg[seg["비율"] >= 12]).mark_text(fontSize=11, fontWeight=600).encode(
        x="mid:Q", y=y, text=alt.Text("비율:Q", format=".0f"),
        color=alt.condition("datum['점수'] == 1 || datum['점수'] == 5",
                            alt.value("white"), alt.value(INK)),
        tooltip=tooltip,
    )
    zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="#8A9794", strokeWidth=1).encode(x="x:Q")
    return _base_config((bars + zero + labels).properties(height=420))


def chart_means(stats: pd.DataFrame):
    d = stats.copy()
    d["label"] = [_qlabel(i, a) for i, a in enumerate(d["영역"], start=1)]
    d["sd"] = d["표준편차"].fillna(0)
    d["lo"] = (d["평균"] - d["sd"]).clip(lower=1)
    d["hi"] = (d["평균"] + d["sd"]).clip(upper=5)
    order = list(d["label"])
    y = alt.Y("label:N", sort=order, title=None, axis=alt.Axis(labelLimit=160, ticks=False, domain=False))
    x_scale = alt.Scale(domain=[1, 5])
    tooltip = [alt.Tooltip("label:N", title="문항"), alt.Tooltip("문항:N", title="내용"),
               alt.Tooltip("평균:Q", format=".2f"), alt.Tooltip("표준편차:Q", format=".2f"),
               alt.Tooltip("응답수:Q")]
    mid = alt.Chart(pd.DataFrame({"x": [3]})).mark_rule(color="#C9D3D0", strokeDash=[4, 4]).encode(x="x:Q")
    sd = alt.Chart(d).mark_rule(color=MINT, strokeWidth=2, opacity=0.55).encode(
        x=alt.X("lo:Q", scale=x_scale), x2="hi:Q", y=y, tooltip=tooltip)
    dots = alt.Chart(d).mark_circle(size=150, color=PINE, opacity=1, stroke="white", strokeWidth=2).encode(
        x=alt.X("평균:Q", scale=x_scale, title="평균 점수 (1 = 전혀 아니다, 5 = 매우 그렇다)",
                axis=alt.Axis(values=[1, 2, 3, 4, 5])),
        y=y, tooltip=tooltip)
    text = alt.Chart(d).mark_text(dy=-13, fontSize=12, fontWeight=700, color=INK).encode(
        x=alt.X("평균:Q", scale=x_scale), y=y, text=alt.Text("평균:Q", format=".2f"))
    return _base_config((mid + sd + dots + text).properties(height=420))


def chart_one(row: pd.Series):
    n = row["응답수"]
    d = pd.DataFrame({
        "응답": LEVEL_LABELS,
        "응답수": [int(row[l]) for l in LEVEL_LABELS],
    })
    d["비율"] = (d["응답수"] / n * 100).round(1) if n else 0
    d["표시"] = d.apply(lambda r: f"{r['응답수']}명 ({r['비율']:.0f}%)", axis=1)
    x = alt.X("응답:N", sort=LEVEL_LABELS, title=None, axis=alt.Axis(labelAngle=0, ticks=False))
    bars = alt.Chart(d).mark_bar(size=46, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=x,
        y=alt.Y("응답수:Q", title="응답 수(명)", axis=alt.Axis(tickMinStep=1, format="d")),
        color=alt.Color("응답:N", scale=alt.Scale(domain=LEVEL_LABELS, range=SCALE_COLORS), legend=None),
        tooltip=[alt.Tooltip("응답:N"), alt.Tooltip("응답수:Q", title="응답 수"),
                 alt.Tooltip("비율:Q", title="비율(%)", format=".1f")],
    )
    text = alt.Chart(d).mark_text(dy=-10, fontSize=12, fontWeight=600, color=INK).encode(
        x=x, y="응답수:Q", text="표시:N")
    return _base_config((bars + text).properties(height=300))


# ====================================================================== Tab 2 결과 시각화
def render_result():
    df = db.fetch_survey_df()
    if df.empty:
        st.info("아직 응답이 없습니다. '설문 응시' 탭에서 첫 번째로 응답해 주세요.")
        return

    stats = compute_stats(df)
    all_scores = df[QCOLS].to_numpy().ravel()
    pos_rate = (all_scores >= 4).mean() * 100

    # ---- 요약
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("응답자 수", f"{len(df)}명", border=True)
    c2.metric("전체 평균", f"{all_scores.mean():.2f} / 5", border=True)
    c3.metric("긍정 응답 비율", f"{pos_rate:.1f}%", help="'그렇다'와 '매우 그렇다'를 고른 비율 (전체 문항)", border=True)
    c4.metric("최근 응답", str(df["created_at"].max())[5:16], border=True)

    best = stats.loc[stats["평균"].idxmax()]
    worst = stats.loc[stats["평균"].idxmin()]
    st.markdown(
        f"가장 긍정적으로 인식한 문항은 **{best['번호']} {best['영역']}**(평균 {best['평균']:.2f})이고, "
        f"가장 낮은 문항은 **{worst['번호']} {worst['영역']}**(평균 {worst['평균']:.2f})입니다."
    )

    # ---- 전체 문항 차트
    left, right = st.columns((3, 2))
    with left:
        st.subheader("문항별 응답 분포")
        st.caption("0을 기준으로 왼쪽은 부정, 오른쪽은 긍정 응답입니다. '보통이다'는 기준선 양쪽에 반씩 놓입니다.")
        st.altair_chart(chart_likert(stats), width="stretch")
    with right:
        st.subheader("문항별 평균")
        st.caption("점은 평균, 옅은 선은 평균 ± 표준편차 범위입니다. 점선은 중간값 3점입니다.")
        st.altair_chart(chart_means(stats), width="stretch")

    # ---- 문항 상세
    st.subheader("문항별 상세 통계")
    options = list(range(len(QUESTIONS)))
    sel = st.selectbox(
        "문항 선택", options,
        format_func=lambda i: f"Q{i + 1}. {QUESTIONS[i][2]}",
        key="survey_detail_q",
    )
    row = stats.iloc[sel]
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("응답 수", f"{row['응답수']}명")
    m2.metric("평균", f"{row['평균']:.2f}")
    m3.metric("표준편차", "-" if pd.isna(row["표준편차"]) else f"{row['표준편차']:.2f}")
    m4.metric("중앙값", f"{row['중앙값']:.1f}")
    m5.metric("긍정 비율", f"{row['긍정 비율(%)']:.1f}%")
    st.altair_chart(chart_one(row), width="stretch")

    # ---- 표 + 다운로드
    st.subheader("전체 통계표")
    st.dataframe(
        stats,
        hide_index=True,
        width="stretch",
        column_config={
            "문항": st.column_config.TextColumn(width="large"),
            "평균": st.column_config.NumberColumn(format="%.2f"),
            "표준편차": st.column_config.NumberColumn(format="%.2f"),
            "긍정 비율(%)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%"),
            "부정 비율(%)": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )
    st.download_button(
        "통계표 CSV 내려받기",
        stats.to_csv(index=False).encode("utf-8-sig"),  # 엑셀에서 한글이 깨지지 않도록 BOM 포함
        file_name="survey_stats.csv",
        mime="text/csv",
    )
