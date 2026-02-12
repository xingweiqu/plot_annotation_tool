"""
Plot Annotation Tool - v5.3 (Single Plot + VAD + Export + Random + Calib + Bilingual)
Features:
1) Absolute scoring for ONE plot on each dimension (1-10), + overall + notes
2) Export CSV + clear annotations
3) Add annotator_id, timestamp, seed_id, method_name + Random Plot button
4) Calibration items (gold plots) + per-annotator z-score normalization helper preview
5) Bilingual (English + Chinese) UI
"""

import streamlit as st
import json
import textwrap
import re
import pandas as pd
from datetime import datetime, timezone
import random

# ---------------- Graphviz (optional) ----------------
try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

# ============== Page Config ==============
st.set_page_config(
    page_title="📖 Plot Annotation Tool | 剧本标注工具",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== Styles ==============
st.markdown("""
<style>
    .paper-sheet {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        padding: 25px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-radius: 4px;
        margin-bottom: 20px;
    }
    .script-text {
        font-family: 'Georgia', 'Times New Roman', serif;
        font-size: 16px;
        line-height: 1.6;
    }
    .script-text h1, .script-text h2, .script-text h3 {
        color: #111 !important;
        border-bottom: 1px solid #ddd;
        padding-bottom: 8px;
        margin-top: 20px;
    }
    .tree-text {
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 14px;
        color: #333 !important;
        white-space: pre-wrap;
    }
    .card-header {
        background: #2D3436;
        color: white;
        padding: 12px;
        border-radius: 6px 6px 0 0;
    }
    [data-testid="stGraphVizChart"] {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============== Utils ==============

def safe_get(plot: dict, key: str, default=""):
    v = plot.get(key, default)
    return default if v is None else v

def get_plot_id(plot: dict) -> str:
    """Stable-ish id for plots: prefer explicit id, else title+seed+method."""
    for k in ["plot_id", "id", "uuid"]:
        if plot.get(k):
            return str(plot[k])
    title = str(plot.get("title", ""))
    seed = str(plot.get("seed_id", plot.get("seed", "")))
    method = str(plot.get("method", plot.get("method_name", plot.get("system", ""))))
    return f"{title}||{seed}||{method}"

def get_graph_data(plot):
    raw = plot.get('causal_graph')
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return None

def parse_tree_text_to_graphviz(tree_text):
    """Text tree -> Graphviz object"""
    if not HAS_GRAPHVIZ or not tree_text:
        return None
    dot = graphviz.Digraph()
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='filled', fillcolor='#E1F5FE',
             fontname='Arial', fontsize='11', margin='0.15')
    dot.attr('edge', color='#666')

    lines = tree_text.split('\n')
    stack = []
    node_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())
        content = stripped.replace('*', '').strip()

        match = re.search(r'\[(.*?)\]', content)
        label = match.group(1) if match else (content[:25] + '..' if len(content) > 25 else content)
        detail = content.replace(match.group(0), '') if match else content

        node_id = f"n{node_count}"
        node_count += 1

        wrap_label = f"<{label}<br/><font point-size='9' color='#555'>{detail[:40]}</font>>"
        dot.node(node_id, label=wrap_label)

        while stack and stack[-1][0] >= indent:
            stack.pop()
        if stack:
            dot.edge(stack[-1][1], node_id)
        stack.append((indent, node_id))

    return dot

def create_causal_chart(data):
    """Causal graph -> Graphviz object"""
    if not HAS_GRAPHVIZ or not data:
        return None
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR', splines='ortho', nodesep='0.4', ranksep='0.6')
    dot.attr('node', fontname='Arial', style='filled', penwidth='0', fontcolor='white')

    nodes = data.get('event_nodes', [])
    edges = data.get('edges', [])

    colors = {
        'milestone': '#00BCD4',
        'escalation': '#66BB6A',
        'climax': '#EF5350',
        'default': '#78909C'
    }

    for n in nodes:
        ntype = str(n.get('type', 'default')).lower()
        c = next((v for k, v in colors.items() if k in ntype), colors['default'])
        name = str(n.get('name', n.get('label', n.get('id', ''))))
        label = "\\n".join(textwrap.wrap(name, 20))
        dot.node(str(n.get('id', name)), label=label, fillcolor=c, shape='box', style='rounded,filled')

    for e in edges:
        et = str(e.get('type', '')).lower()
        color = '#FF7043' if et == 'catalyst' else '#455A64'
        style = 'dashed' if et == 'concurrent' else 'solid'
        dot.edge(str(e.get('from')), str(e.get('to')), color=color, style=style)

    return dot

# ============== State ==============

def init_state():
    if 'plots' not in st.session_state:
        st.session_state.plots = []
    if 'annotations' not in st.session_state:
        st.session_state.annotations = []
    if 'gold_ids' not in st.session_state:
        st.session_state.gold_ids = set()
    if 'sel_idx' not in st.session_state:
        st.session_state.sel_idx = 0

def load_json(files):
    """Load JSON plots, simple de-dup by plot_id."""
    existing_ids = set(get_plot_id(p) for p in st.session_state.plots)
    for f in files:
        try:
            content = json.load(f)
            items = content if isinstance(content, list) else [content]
            for item in items:
                pid = get_plot_id(item)
                if pid not in existing_ids:
                    st.session_state.plots.append(item)
                    existing_ids.add(pid)
        except Exception:
            continue

# ============== Rendering ==============

def render_card(plot):
    with st.container():
        st.markdown(f"""
        <div style="border:1px solid #ddd; border-radius:6px; background:white; margin-bottom:20px;">
            <div class="card-header">
                <h4 style="margin:0; color:white;">{safe_get(plot,'title','Untitled')}</h4>
                <div style="font-size:0.8em; opacity:0.9;">
                    {safe_get(plot,'genre','')} | {safe_get(plot,'status','')} |
                    seed={safe_get(plot,'seed_id', safe_get(plot,'seed',''))} |
                    method={safe_get(plot,'method_name', safe_get(plot,'method',''))}
                </div>
            </div>
            <div style="padding:15px;">
        """, unsafe_allow_html=True)

        t0, t1, t2, t3 = st.tabs([
            "📋 Input / 设定输入", 
            "🗺️ Causal Graph / 因果图", 
            "🌳 Story Tree / 故事树", 
            "📜 Full Script / 完整剧本"
        ])

        with t0:
            # 显示 inputs 数据
            st.markdown("#### 🕐 Time & Location / 时间 & 地点")
            time_val = safe_get(plot, 'time', '')
            location_val = safe_get(plot, 'location', '')
            if time_val or location_val:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Time / 时间:** {time_val if time_val else 'Not specified / 未指定'}")
                with col2:
                    st.markdown(f"**Location / 地点:** {location_val if location_val else 'Not specified / 未指定'}")
            else:
                st.info("No time/location info / 无时间/地点信息")

            st.markdown("#### 🎭 Setting / 场景设定")
            setting_val = safe_get(plot, 'setting', '')
            if setting_val:
                st.markdown(f'<div class="paper-sheet"><div class="script-text">{setting_val}</div></div>', unsafe_allow_html=True)
            else:
                st.info("No setting info / 无场景设定")

            st.markdown("#### 👥 Characters / 角色列表")
            characters = plot.get('characters', [])
            if characters and isinstance(characters, list) and len(characters) > 0:
                for char in characters:
                    if isinstance(char, dict):
                        name = char.get('name', 'Unknown / 未知')
                        desc = char.get('description', 'No description / 无描述')
                        st.markdown(f"**{name}**: {desc}")
                    else:
                        st.markdown(f"- {char}")
            else:
                st.info("No character info / 无角色信息")

            st.markdown("#### 📖 Background / 背景故事")
            background_val = safe_get(plot, 'background', '')
            if background_val:
                st.markdown(f'<div class="paper-sheet"><div class="script-text">{background_val}</div></div>', unsafe_allow_html=True)
            else:
                st.info("No background info / 无背景故事")

            # 显示作者信息（如果有）
            author_val = safe_get(plot, 'author', '')
            if author_val and author_val != 'Unknown':
                st.markdown(f"**Author / 作者:** {author_val}")

        with t1:
            g_data = get_graph_data(plot)
            if g_data:
                chart = create_causal_chart(g_data)
                if chart:
                    st.graphviz_chart(chart, use_container_width=True)
                    with st.expander("🔍 Enlarge / Fullscreen / 放大查看"):
                        st.graphviz_chart(chart, use_container_width=True)
                else:
                    st.info("Graphviz not installed or graph data unavailable / Graphviz 未安装或图数据不可用")
            else:
                st.info("No causal graph data / 无因果图数据")

        with t2:
            tree_txt = safe_get(plot, 'pruned_tree', '')
            if tree_txt:
                chart_tree = parse_tree_text_to_graphviz(tree_txt)
                if chart_tree:
                    st.graphviz_chart(chart_tree, use_container_width=True)
                    with st.expander("🔍 Enlarge Tree / 放大树状图"):
                        st.graphviz_chart(chart_tree, use_container_width=True)

                st.markdown('<div class="paper-sheet"><div class="tree-text">', unsafe_allow_html=True)
                st.text(tree_txt)
                st.markdown('</div></div>', unsafe_allow_html=True)
            else:
                st.info("No story tree / 无故事树")

        with t3:
            final_plot = safe_get(plot, 'final_plot', '')
            if final_plot:
                st.markdown('<div class="paper-sheet"><div class="script-text">', unsafe_allow_html=True)
                st.markdown(final_plot)
                st.markdown('</div></div>', unsafe_allow_html=True)
            else:
                st.warning("No script available / 暂无剧本")

        st.markdown("</div></div>", unsafe_allow_html=True)

# ============== Calibration / Normalization Helpers ==============

def make_df():
    if not st.session_state.annotations:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.annotations)

def per_annotator_zscore_preview(df: pd.DataFrame):
    """
    For each annotator, compute mean/std on calibration items only (if exist),
    then show z-scored overall for non-calibration. Preview only.
    """
    if df.empty:
        return df
    if "annotator_id" not in df.columns or "is_calibration" not in df.columns:
        return df

    out = df.copy()
    out["overall_z"] = None

    for aid, g in out.groupby("annotator_id"):
        calib = g[g["is_calibration"] == True]
        if len(calib) >= 2:
            mu = calib["overall"].mean()
            sd = calib["overall"].std(ddof=0)
            if sd == 0:
                sd = 1.0
            idx = (out["annotator_id"] == aid) & (out["is_calibration"] == False)
            out.loc[idx, "overall_z"] = (out.loc[idx, "overall"] - mu) / sd

    return out

# ============== Main ==============

def main():
    init_state()
    st.title("🚀 Plot Annotation Tool | 剧本标注工具 (v5.3)")

    # ---- Dimensions (now includes full VAD) ----
    dims = [
        ("Surprise", "Novelty/twists/unpredictability | 剧情新意/反转/不可预测性"),
        ("Valence", "Emotional direction (positive vs negative) | 情绪正负方向"),
        ("Arousal", "Emotional intensity/tension | 情绪强度/紧张度"),
        ("Dominance", "Control/agency of characters | 角色掌控感/主导权"),
        ("Conflict", "Conflict intensity & diversity | 冲突强度与多样性"),
        ("Coherence", "Causal consistency & plausibility | 因果自洽与整体合理性"),
    ]

    # --- Sidebar ---
    with st.sidebar:
        st.subheader("👤 Annotator / 标注者")
        annotator_id = st.text_input(
            "Annotator ID (required) / 标注者ID（必填）", 
            value=st.session_state.get("annotator_id", "")
        )
        st.session_state.annotator_id = annotator_id

        st.divider()
        st.subheader("📂 Data Upload / 数据上传")
        files = st.file_uploader(
            "JSON Files / JSON 文件", 
            accept_multiple_files=True
        )
        if files:
            load_json(files)

        st.metric("Plots Loaded / 已加载剧本", len(st.session_state.plots))
        st.metric("Annotations Saved / 已保存标注", len(st.session_state.annotations))

        if st.button("🗑️ Clear All Plots / 清空所有剧本"):
            st.session_state.plots = []
            st.session_state.gold_ids = set()
            st.session_state.sel_idx = 0
            st.rerun()

        if st.button("🗑️ Clear All Annotations / 清空所有标注"):
            st.session_state.annotations = []
            st.rerun()

        st.divider()
        st.subheader("🏆 Calibration (Gold) / 校准题")
        st.caption("Select 1-3 plots as calibration items (for normalizing scales across annotators) / 选择 1-3 个 plot 作为校准题（用于归一化不同标注者的尺度）")
        if st.session_state.plots:
            title_map = {f"{i}: {safe_get(p,'title','Untitled')}": get_plot_id(p)
                         for i, p in enumerate(st.session_state.plots)}
            gold_keys = st.multiselect(
                "Select Gold Plots / 选择校准剧本",
                options=list(title_map.keys()),
                default=[],
            )
            st.session_state.gold_ids = set(title_map[k] for k in gold_keys)

    # --- Need data ---
    if len(st.session_state.plots) < 1:
        st.info("👈 Please upload at least 1 JSON file / 请上传至少 1 个 JSON 文件")
        return

    # --- Plot Selection ---
    titles = [safe_get(p, "title", f"Plot {i}") for i, p in enumerate(st.session_state.plots)]
    max_idx = len(titles) - 1

    top = st.columns([1, 1, 3])
    with top[0]:
        idx = st.selectbox(
            "Select Plot / 选择剧本",
            range(len(titles)),
            index=int(st.session_state.sel_idx),
            format_func=lambda i: titles[i],
            key="sel_plot"
        )
    with top[1]:
        if st.button("🎲 Random Plot / 随机选择"):
            st.session_state.sel_idx = random.randint(0, max_idx)
            st.rerun()
    with top[2]:
        st.caption("Tip: Random Plot reduces selection bias; Gold plots calibrate annotator scales. / 提示：随机选择可减少挑选偏差；校准题用于归一化不同标注者的尺度。")

    st.session_state.sel_idx = int(idx)

    plot = st.session_state.plots[st.session_state.sel_idx]
    render_card(plot)

    # --- Scoring Form ---
    st.divider()
    st.subheader("⚖️ Scoring / Annotation (1-10) | 评分 / 标注（1-10）")

    if not st.session_state.get("annotator_id"):
        st.warning("Please fill in annotator_id on the left sidebar (required) before submitting. / 请先在左侧填写 annotator_id（必填），否则不允许提交。")
        return

    pid = get_plot_id(plot)
    is_calibration = (pid in st.session_state.gold_ids)

    seed = safe_get(plot, "seed_id", safe_get(plot, "seed", ""))
    method = safe_get(plot, "method_name", safe_get(plot, "method", safe_get(plot, "system", "")))

    with st.form("score_form", clear_on_submit=False):
        if is_calibration:
            st.info("🟨 This is a Gold Plot (calibration item): will be marked as is_calibration=True / 当前 Plot 是校准题：该条记录会标记为 is_calibration=True")

        st.markdown("Rate the **current plot** absolutely (1=very poor, 10=excellent). / 对 **当前剧本** 绝对打分（1=很差，10=非常好）。")

        scores = {}
        for key, desc in dims:
            scores[key] = st.slider(
                f"{key} ({desc})",
                min_value=1, max_value=10, value=6, step=1,
                key=f"S_{key}"
            )

        st.markdown("---")
        overall = st.slider(
            "Overall (Overall rating) / 整体评价", 
            1, 10, 6, 1, 
            key="Overall"
        )
        confidence = st.select_slider(
            "Confidence (Your certainty about this rating) / 置信度（你对本次评分的把握）",
            options=["low", "mid", "high"],
            value="mid",
            key="Confidence"
        )
        notes = st.text_area(
            "Notes (Optional: brief reasoning / failure modes / use cases) / 备注（可选：一句话理由 / 失败模式 / 适用场景）",
            key="Notes",
            height=120
        )

        submitted = st.form_submit_button("✅ Submit Annotation / 提交标注")

        if submitted:
            now = datetime.now(timezone.utc).isoformat()

            row = {
                "timestamp_utc": now,
                "annotator_id": st.session_state.annotator_id,
                "is_calibration": bool(is_calibration),

                "plot_id": pid,
                "plot_title": safe_get(plot, "title", ""),
                "plot_genre": safe_get(plot, "genre", ""),
                "plot_status": safe_get(plot, "status", ""),
                "seed_id": seed,
                "method_name": method,

                "overall": int(overall),
                "confidence": confidence,
                "notes": notes.strip(),
            }

            for k, _ in dims:
                row[k] = int(scores[k])

            st.session_state.annotations.append(row)
            st.success(f"Annotation saved ✅ Total: {len(st.session_state.annotations)} / 已保存标注 ✅ 当前累计 {len(st.session_state.annotations)} 条")

    # --- Data Preview / Export ---
    st.divider()
    st.subheader("📊 Collected Annotations (Preview / Export / Normalization) | 已收集标注（预览 / 导出 / 归一化）")

    df = make_df()
    if df.empty:
        st.info("No annotations yet. / 还没有任何标注记录。")
        return

    st.dataframe(df, use_container_width=True, height=320)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download CSV (raw) / 下载 CSV（原始数据）",
        data=csv_bytes,
        file_name="plot_annotations_raw.csv",
        mime="text/csv"
    )

    # --- Normalization preview based on calibration items ---
    st.markdown("### 🧪 Normalization Preview (based on Gold/Calibration) | 归一化预览（基于校准题）")
    st.caption("Preview only: for each annotator, z-score using mean/std from their calibration records. / 仅预览：对每个标注者，用其校准题的 overall 均值/方差做 z-score。")
    df_norm = per_annotator_zscore_preview(df)

    show_cols = [
        "timestamp_utc", "annotator_id", "is_calibration",
        "plot_title", "overall", "overall_z", "confidence", "notes"
    ]
    show_cols = [c for c in show_cols if c in df_norm.columns]
    st.dataframe(df_norm[show_cols], use_container_width=True, height=260)

    csv_norm = df_norm.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download CSV (with overall_z) / 下载 CSV（含归一化分数）",
        data=csv_norm,
        file_name="plot_annotations_with_overall_z.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
