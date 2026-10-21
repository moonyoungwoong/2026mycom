"""
ui.py - 화면 꾸미기
 - inject_css()      : Streamlit 기본 위젯/사이드바 스타일 (CSS)
 - render_navbar()   : Tailwind + Alpine.js 로 만든 상단바와 햄버거(☰) 버튼
 - render_sidebar()  : 좌측 슬라이드 메뉴 (로그인 전/후 메뉴가 다름)
 - guest_hero(), dashboard_hero() : 로그인 전/후 랜딩페이지 상단 영역

참고) Tailwind, Alpine.js는 st.components.v1.html 로 만든 iframe 안에서 CDN으로 불러옵니다.
     인터넷이 연결되어 있어야 디자인이 정상적으로 보입니다.
"""
import html
import json

import streamlit as st
import streamlit.components.v1 as components

import auth

# 색상 토큰
PINE = "#0F3D3E"   # 사이드바, 진한 배경
MINT = "#3FB39A"   # 주요 버튼, 강조
MIST = "#EEF3F2"   # 페이지 배경
INK = "#16222A"    # 본문 글자
AMBER = "#F2B544"  # 작은 포인트

FONT_CSS = "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css"
HEAD = f"""
<script src="https://cdn.tailwindcss.com"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js"></script>
<link rel="stylesheet" href="{FONT_CSS}">
<script>
  tailwind.config = {{ theme: {{ extend: {{
    colors: {{ pine: '{PINE}', mint: '{MINT}', mist: '{MIST}', ink: '{INK}', amber: '{AMBER}' }},
    fontFamily: {{ sans: ['Pretendard', 'system-ui', 'sans-serif'] }}
  }} }} }};
</script>
<style>
  html, body {{ margin: 0; background: transparent; font-family: Pretendard, system-ui, sans-serif; }}
  [x-cloak] {{ display: none !important; }}
  @media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; animation: none !important; }} }}
</style>
"""


def show_html(page: str, height) -> None:
    """HTML 조각을 iframe으로 표시합니다.
    최신 Streamlit(1.50+)은 st.iframe, 이전 버전은 components.html을 사용합니다.
    (두 방식 모두 iframe 안의 스크립트가 부모 페이지의 사이드바 버튼에 접근할 수 있습니다.)"""
    if hasattr(st, "iframe"):
        st.iframe(page, height=height)
    else:
        components.html(page, height=600 if height == "content" else height, scrolling=height == "content")


def e(text) -> str:
    """HTML 이스케이프 (사용자 입력을 화면에 그릴 때 XSS 방지)"""
    return html.escape(str(text))


# ------------------------------------------------------------------ CSS
def inject_css() -> None:
    st.markdown(
        f"""
<style>
@import url('{FONT_CSS}');
html, body, .stApp, .stMarkdown, input, textarea, button, label, p, h1, h2, h3 {{
  font-family: 'Pretendard', system-ui, sans-serif;
}}
.stApp {{ background: {MIST}; color: {INK}; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.2rem; max-width: 1180px; }}
h1 {{ letter-spacing: -0.02em; font-weight: 800; }}

/* ---------- 좌측 슬라이드 메뉴 ---------- */
section[data-testid="stSidebar"] {{
  background: {PINE};
  transition: transform .35s cubic-bezier(.2,.8,.2,1), width .35s cubic-bezier(.2,.8,.2,1),
              min-width .35s cubic-bezier(.2,.8,.2,1), margin .35s cubic-bezier(.2,.8,.2,1);
}}
section[data-testid="stSidebar"] * {{ color: #E6F2EF; }}
section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.12); }}
section[data-testid="stSidebar"] .stButton > button {{
  width: 100%; justify-content: flex-start; text-align: left;
  background: transparent; border: 0; border-radius: 10px;
  padding: .6rem .85rem; font-weight: 500; transition: background .2s;
}}
section[data-testid="stSidebar"] .stButton > button div {{ justify-content: flex-start; }}
section[data-testid="stSidebar"] .stButton > button:hover {{ background: rgba(255,255,255,.08); }}
section[data-testid="stSidebar"] .stButton > button:focus-visible {{ outline: 2px solid {AMBER}; }}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
  background: rgba(63,179,154,.22); box-shadow: inset 3px 0 0 {MINT};
}}
.menu-caption {{ font-size: .75rem; opacity: .6; margin: 1rem 0 .3rem .4rem; }}
.side-user {{ display:flex; gap:.7rem; align-items:center; padding:.8rem; border-radius:12px;
  background: rgba(255,255,255,.06); }}
.side-avatar {{ width:38px; height:38px; border-radius:50%; background:{AMBER}; color:{PINE} !important;
  display:flex; align-items:center; justify-content:center; font-weight:800; }}

/* ---------- 본문 위젯 ---------- */
.stButton > button[kind="primary"], .stFormSubmitButton > button {{
  background: {MINT}; border: 0; color: white; border-radius: 10px; font-weight: 600;
}}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover {{ background: #33977f; color: white; }}
[data-testid="stForm"] {{
  background: white; border: 1px solid #D6E2DF; border-radius: 18px; padding: 1.6rem 1.6rem 1rem;
}}
[data-testid="stExpander"] {{ background: white; border-radius: 14px; border: 1px solid #D6E2DF; }}
iframe {{ border: 0; }}
</style>
""",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------ 상단바 + 햄버거
def render_navbar() -> None:
    user = st.session_state.get("user")
    if user:
        right = f"""
        <div class="flex items-center gap-2">
          <span class="hidden sm:inline text-sm text-slate-500">로그인됨</span>
          <span class="w-2 h-2 rounded-full bg-mint"></span>
          <span class="font-semibold text-ink">{e(user['username'])}</span>
          <span class="w-9 h-9 rounded-full bg-amber text-pine font-extrabold flex items-center justify-center">{e(user['username'][:1])}</span>
        </div>"""
    else:
        right = """<span class="text-sm text-slate-500">로그인이 필요합니다</span>"""

    show_html(
        f"""<!DOCTYPE html><html><head>{HEAD}</head><body>
<nav x-data="nav()" x-init="init()"
     class="flex items-center justify-between bg-white border border-[#D6E2DF] rounded-2xl px-3 py-2">
  <div class="flex items-center gap-3">
    <!-- 햄버거 버튼: 클릭하면 Streamlit 좌측 사이드바를 열고/닫습니다 -->
    <button @click="toggle()" :aria-expanded="open" aria-label="메뉴 열기/닫기"
            class="w-11 h-11 rounded-xl hover:bg-mist focus-visible:outline focus-visible:outline-2 focus-visible:outline-mint
                   flex flex-col items-center justify-center gap-1.5">
      <span class="block h-0.5 w-5 bg-ink rounded transition duration-300" :class="open && 'translate-y-2 rotate-45'"></span>
      <span class="block h-0.5 w-5 bg-ink rounded transition duration-300" :class="open && 'opacity-0'"></span>
      <span class="block h-0.5 w-5 bg-ink rounded transition duration-300" :class="open && '-translate-y-2 -rotate-45'"></span>
    </button>
    <span class="text-lg font-extrabold tracking-tight text-pine">MyProject</span>
  </div>
  {right}
</nav>
<script>
function nav() {{
  return {{
    open: false,
    doc() {{ try {{ return window.parent.document; }} catch (err) {{ return null; }} }},
    sidebar() {{ const d = this.doc(); return d && d.querySelector('section[data-testid="stSidebar"]'); }},
    sync() {{
      const s = this.sidebar();
      if (!s) {{ this.open = false; return; }}
      const a = s.getAttribute('aria-expanded');
      this.open = a !== null ? a === 'true' : s.getBoundingClientRect().right > 60;
    }},
    init() {{ this.sync(); setInterval(() => this.sync(), 400); }},
    toggle() {{
      const d = this.doc(); if (!d) return;
      this.sync();
      // Streamlit 버전마다 버튼 이름이 달라 여러 후보를 차례로 찾습니다.
      const targets = this.open
        ? ['[data-testid="stSidebarCollapseButton"] button', '[data-testid="stSidebarCollapseButton"]']
        : ['[data-testid="stExpandSidebarButton"]', '[data-testid="stSidebarCollapsedControl"] button',
           '[data-testid="collapsedControl"] button'];
      for (const q of targets) {{ const b = d.querySelector(q); if (b) {{ b.click(); break; }} }}
      setTimeout(() => this.sync(), 380);
    }}
  }};
}}
</script>
</body></html>""",
        72,
    )


# ------------------------------------------------------------------ 좌측 메뉴
def _menu_button(label: str, page: str, key: str) -> None:
    active = st.session_state.page == page
    st.button(label, key=key, type="primary" if active else "secondary",
              on_click=auth.go, args=(page,), width="stretch")


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### MyProject")
        if auth.is_logged_in():
            u = st.session_state.user
            st.markdown(
                f"""<div class="side-user"><div class="side-avatar">{e(u['username'][:1])}</div>
                <div><div style="font-weight:700">{e(u['username'])}</div>
                <div style="font-size:.8rem;opacity:.7">@{e(u['userid'])}</div></div></div>""",
                unsafe_allow_html=True,
            )
            st.markdown('<div class="menu-caption">메뉴</div>', unsafe_allow_html=True)
            _menu_button("🏠  홈", "home", "m_home")
            _menu_button("📋  설문 참여", "survey", "m_survey")
            _menu_button("👤  내 정보", "profile", "m_profile")
            st.divider()
            st.button("🚪  로그아웃", key="m_logout", on_click=auth.logout, width="stretch")
        else:
            st.markdown('<div class="menu-caption">시작하기</div>', unsafe_allow_html=True)
            _menu_button("🏠  처음 화면", "landing", "m_landing")
            _menu_button("📝  사용자 등록", "register", "m_register")
            _menu_button("🔐  로그인", "login", "m_login")
            _menu_button("🔐  파이썬IDE", "pythonide", "m_pythonide")
            



# ------------------------------------------------------------------ 로그인 전 랜딩
def guest_hero(user_count: int) -> None:
    show_html(
        f"""<!DOCTYPE html><html><head>{HEAD}</head><body>
<section class="bg-pine text-white rounded-3xl px-7 py-9 md:px-12 md:py-12 overflow-hidden relative"
         x-data="{{ words: ['내 정보를 안전하게', '데이터를 한곳에', '어디서든 간편하게'], i: 0 }}"
         x-init="setInterval(() => i = (i + 1) % words.length, 2600)">
  <div class="absolute -right-16 -top-16 w-64 h-64 rounded-full border-[28px] border-mint/30"></div>
  <p class="text-amber font-semibold mb-3">나의 첫 번째 웹앱</p>
  <h1 class="text-4xl md:text-6xl font-extrabold leading-[1.1] tracking-tight max-w-2xl">
    로그인하고<br>
    <span class="inline-block min-h-[1.2em]">
      <template x-for="(w, idx) in words" :key="idx">
        <span x-show="i === idx" x-cloak
              x-transition:enter="transition duration-500" x-transition:enter-start="opacity-0 translate-y-3"
              x-transition:enter-end="opacity-100 translate-y-0" class="inline-block" x-text="w"></span>
      </template>
    </span>
  </h1>
  <p class="mt-5 text-white/75 max-w-xl leading-relaxed">
    회원으로 등록하면 이름, 나이, 주소, 연락처를 저장하고 동영상 콘텐츠를 볼 수 있습니다.
    현재 등록된 사용자는 <b class="text-white">{user_count}명</b>입니다.
  </p>
  <ol class="mt-9 grid gap-4 sm:grid-cols-3 text-sm">
    <li class="flex gap-3"><span class="w-7 h-7 shrink-0 rounded-full bg-mint flex items-center justify-center font-bold">1</span>
      <span class="text-white/85">왼쪽 메뉴(☰)에서 <b class="text-white">사용자 등록</b></span></li>
    <li class="flex gap-3"><span class="w-7 h-7 shrink-0 rounded-full bg-mint flex items-center justify-center font-bold">2</span>
      <span class="text-white/85">아이디와 비밀번호로 <b class="text-white">로그인</b></span></li>
    <li class="flex gap-3"><span class="w-7 h-7 shrink-0 rounded-full bg-mint flex items-center justify-center font-bold">3</span>
      <span class="text-white/85">내 정보를 입력하고 <b class="text-white">DB 확인</b></span></li>
  </ol>
</section>
</body></html>""",
        "content",
    )


# ------------------------------------------------------------------ 로그인 후 랜딩
def dashboard_hero(user: dict, total_users: int, total_rows: int, my_rows: int) -> None:
    stats = json.dumps([
        {"label": "전체 사용자", "value": total_users, "unit": "명"},
        {"label": "전체 데이터", "value": total_rows, "unit": "건"},
        {"label": "내가 입력한 데이터", "value": my_rows, "unit": "건"},
    ], ensure_ascii=False)
    show_html(
        f"""<!DOCTYPE html><html><head>{HEAD}</head><body>
<section class="bg-white border border-[#D6E2DF] rounded-3xl p-6 md:p-8 flex flex-col md:flex-row md:items-end gap-6 md:justify-between"
  x-data="dash({e(stats)})" x-init="start()">
  <div>
    <p class="text-slate-500" x-text="greeting"></p>
    <h1 class="text-3xl md:text-4xl font-extrabold tracking-tight text-pine mt-1">{e(user['username'])}님, 반가워요</h1>
    <p class="mt-2 text-slate-500 text-sm">가입일 {e(str(user['created_at'])[:10])}, 지금 <span x-text="clock" class="tabular-nums"></span></p>
  </div>
  <dl class="flex divide-x divide-[#D6E2DF]">
    <template x-for="s in stats" :key="s.label">
      <div class="px-5 first:pl-0">
        <dt class="text-xs text-slate-500" x-text="s.label"></dt>
        <dd class="text-3xl font-extrabold text-ink tabular-nums">
          <span x-text="s.shown"></span><span class="text-base font-semibold text-slate-400 ml-0.5" x-text="s.unit"></span>
        </dd>
      </div>
    </template>
  </dl>
</section>
<script>
function dash(stats) {{
  return {{
    stats: stats.map(s => ({{ ...s, shown: 0 }})),
    clock: '', greeting: '',
    start() {{
      const h = new Date().getHours();
      this.greeting = h < 12 ? '좋은 아침입니다' : h < 18 ? '좋은 오후입니다' : '좋은 저녁입니다';
      const tick = () => this.clock = new Date().toLocaleTimeString('ko-KR');
      tick(); setInterval(tick, 1000);
      // 숫자가 0부터 올라가는 효과 (한 번만)
      const t0 = performance.now(), dur = 900;
      const step = now => {{
        const p = Math.min((now - t0) / dur, 1);
        this.stats.forEach(s => s.shown = Math.round(s.value * (1 - Math.pow(1 - p, 3))));
        if (p < 1) requestAnimationFrame(step);
      }};
      requestAnimationFrame(step);
    }}
  }};
}}
</script>
</body></html>""",
        "content",
    )
