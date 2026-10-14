import streamlit as st
from sympy import symbols
from sympy.logic.boolalg import SOPform, POSform, simplify_logic
from itertools import product
import pandas as pd

st.set_page_config(page_title="Digital Electronics K-Map Solver", page_icon="⚡", layout="wide")

st.markdown("""
<style>
:root { color-scheme: light; }
.block-container { padding-top: 1.8rem; max-width: 1200px; }
.hero { padding: 2.1rem; border-radius: 20px; background: linear-gradient(120deg,#102a43,#176b87); color: white; margin-bottom: 1.2rem; }
.hero h1 { color: white; font-size: 2.3rem; margin-bottom: .35rem; }
.hero p { color: #e2f4ff; font-size: 1.05rem; }
.tag { display:inline-block; padding:.25rem .7rem; margin:.2rem .25rem .2rem 0; border-radius:99px; background:#e7f5ff; color:#075985; font-size:.85rem; }
.card { padding: 1rem 1.2rem; border:1px solid #dbe5ee; border-radius:14px; background:#fbfdff; }
[data-testid="stMetric"] { background:#f2f8fc; padding:1rem; border-radius:12px; }
</style>
""", unsafe_allow_html=True)

VARS = {2: ["A", "B"], 3: ["A", "B", "C"], 4: ["A", "B", "C", "D"]}
GRAY = {1: ["0", "1"], 2: ["00", "01", "11", "10"]}

def gray_codes(bits):
    if bits == 1:
        return ["0", "1"]
    if bits == 2:
        return ["00", "01", "11", "10"]
    raise ValueError("Only 1- and 2-bit Gray codes are used in supported maps.")

def make_map(n, minterms, dontcares):
    vars_ = VARS[n]
    row_bits = n // 2
    col_bits = n - row_bits
    rows, cols = gray_codes(row_bits), gray_codes(col_bits)
    values = []
    for r in rows:
        row = []
        for c in cols:
            idx = int(r + c, 2)
            row.append("X" if idx in dontcares else ("1" if idx in minterms else "0"))
        values.append(row)
    return rows, cols, values

def expr_to_text(expr):
    # SymPy's standard Boolean notation is readable in the report.
    return str(expr).replace("~", "¬").replace("&", "·").replace("|", " + ")

def sop_term_explanation(expr, var_names):
    from sympy.logic.boolalg import Or, And, Not
    terms = list(expr.args) if expr.func == Or else [expr]
    if expr == False:
        return ["The function is 0 for every input, so the minimized expression is 0."]
    if expr == True:
        return ["The function is 1 for every input, so the minimized expression is 1."]
    steps = []
    for i, term in enumerate(terms, 1):
        factors = list(term.args) if term.func == And else [term]
        literals = []
        for f in factors:
            if f.func == Not:
                literals.append(f"¬{f.args[0]}")
            else:
                literals.append(str(f))
        steps.append(f"Product term {i}: " + " · ".join(literals))
    steps.append("OR the product terms to obtain the minimized Sum-of-Products expression.")
    return steps

st.markdown("""
<div class="hero">
  <div class="tag">ECE • Academic Project</div><div class="tag">2–4 Variables</div>
  <h1>⚡ Digital Electronics K-Map Solver</h1>
  <p>Interactive Karnaugh-map visualization, Boolean minimization, and a guided solution summary.</p>
  <hr style="border-color:#6b9eb5">
  <b>C. V. Raman Global University</b><br>
  Department of Electronics and Communication Engineering (ECE)<br>
  <b>Student:</b> Amit Kumar Patra &nbsp; | &nbsp; <b>Registration No.:</b> 2501020717
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Project Information")
    st.write("**C. V. Raman Global University**")
    st.write("Electronics and Communication Engineering")
    st.write("**Student:** Amit Kumar Patra")
    st.write("**Registration:** 2501020717")
    st.divider()
    st.caption("No unofficial college logo is used.")
    st.caption("Academic tool for learning Boolean minimization.")

st.subheader("Start Solving")
left, right = st.columns([1, 1.3])
with left:
    n = st.selectbox("Number of variables", [2, 3, 4], index=2)
    names = VARS[n]
    st.caption("Variable order: " + ", ".join(names))
    mode = st.radio("Input method", ["Minterms (Σm)", "Maxterms (ΠM)"], horizontal=True)
    max_idx = (1 << n) - 1
    entered = st.text_input("Enter indices, comma-separated", placeholder="Example: 1,3,5,7")
    dc_text = st.text_input("Don't-care indices (optional)", placeholder="Example: 2,6")
    form = st.radio("Simplification form", ["Sum of Products (SOP)", "Product of Sums (POS)"], horizontal=False)
    solve = st.button("✨ Solve K-Map", type="primary", use_container_width=True)

def parse_indices(raw, label):
    raw = raw.strip()
    if not raw:
        return []
    try:
        nums = sorted(set(int(x.strip()) for x in raw.split(",") if x.strip() != ""))
    except ValueError:
        raise ValueError(f"{label} must contain integers separated by commas.")
    if any(x < 0 or x > max_idx for x in nums):
        raise ValueError(f"{label} values must be between 0 and {max_idx}.")
    return nums

with right:
    st.markdown("#### Quick guide")
    st.markdown("""
    <div class="card">
    <b>How to use</b><br>
    1. Choose 2, 3, or 4 variables.<br>
    2. Enter minterm or maxterm indices, such as <code>1,3,5,7</code>.<br>
    3. Optionally enter don't-care terms.<br>
    4. Select SOP or POS and press <b>Solve K-Map</b>.<br><br>
    <b>Gray-code order</b><br>
    Two-bit axes use <code>00, 01, 11, 10</code>. Adjacent cells differ in one bit, including wrap-around edges.
    </div>
    """, unsafe_allow_html=True)
    st.info("Index convention: binary index follows the displayed variable order (A is the most significant bit).")

if solve:
    try:
        terms = parse_indices(entered, "Input indices")
        dc = parse_indices(dc_text, "Don't-care indices")
        if set(terms) & set(dc):
            raise ValueError("An index cannot be both an input term and a don't-care.")
        if not terms and not dc:
            raise ValueError("Enter at least one minterm/maxterm or don't-care index.")
        symbols_ = symbols(" ".join(names))
        if not isinstance(symbols_, tuple):
            symbols_ = (symbols_,)
        if mode == "Minterms (Σm)":
            minterms = terms
            maxterms = sorted(set(range(1 << n)) - set(minterms) - set(dc))
        else:
            maxterms = terms
            minterms = sorted(set(range(1 << n)) - set(maxterms) - set(dc))
        rows, cols, grid = make_map(n, minterms, dc)
        st.divider()
        st.subheader("Karnaugh Map")
        st.caption(f"Rows: {', '.join(rows)}  •  Columns: {', '.join(cols)}  •  Cells show 1, 0, or X (don't care).")
        df = pd.DataFrame(grid, index=rows, columns=cols)
        df.index.name = "Gray row"
        st.dataframe(df, use_container_width=True)
        st.caption("Cell index is the binary value of row bits concatenated with column bits.")

        expr_sop = SOPform(symbols_, minterms, dc)
        expr_pos = POSform(symbols_, minterms, dc)
        expr = expr_sop if form.startswith("Sum") else expr_pos
        st.subheader("Simplified Boolean Expression")
        st.success(f"{form}:  **{expr_to_text(expr)}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Variables", n)
        c2.metric("Specified terms", len(terms))
        c3.metric("Don't-care terms", len(dc))
        with st.expander("Step-by-step solution", expanded=True):
            st.markdown("**Step 1 — Define the function**")
            if mode == "Minterms (Σm)":
                st.latex(r"F(" + ",".join(names) + r") = \Sigma m(" + ",".join(map(str, terms)) + ")")
            else:
                st.latex(r"F(" + ",".join(names) + r") = \Pi M(" + ",".join(map(str, terms)) + ")")
            st.markdown("**Step 2 — Fill the K-Map**")
            st.write("Place 1s for minterms, 0s for maxterms, and X for don't-care cells. The map above uses Gray-code order.")
            st.markdown("**Step 3 — Form largest valid groups**")
            st.write("Adjacent 1-cells are grouped in powers of two (1, 2, 4, 8, …); groups may wrap around edges. Don't-care cells may be used when they help simplify the expression.")
            st.markdown("**Step 4 — Read and minimize the expression**")
            st.write("The Boolean minimizer finds a simplified equivalent expression. In SOP, each product term corresponds to a group of 1s; in POS, sum terms correspond to groups of 0s.")
            st.markdown("**SOP result:**")
            st.code(expr_to_text(expr_sop))
            st.markdown("**POS result:**")
            st.code(expr_to_text(expr_pos))
            st.markdown("**SOP term interpretation**")
            for item in sop_term_explanation(expr_sop, names):
                st.write("• " + item)
        report = f"""Digital Electronics K-Map Solver
C. V. Raman Global University
Department: Electronics and Communication Engineering (ECE)
Student: Amit Kumar Patra
Registration Number: 2501020717

Variables: {', '.join(names)}
Input mode: {mode}
Entered indices: {terms}
Don't-care indices: {dc}
K-Map (rows={rows}, columns={cols}):
{df.to_string()}
Simplified SOP: {expr_to_text(expr_sop)}
Simplified POS: {expr_to_text(expr_pos)}
Selected form: {form}
Selected expression: {expr_to_text(expr)}
"""
        st.download_button("⬇️ Download solution report (.txt)", report, file_name="kmap_solution_report.txt", mime="text/plain")
    except Exception as e:
        st.error(str(e))

st.divider()
st.markdown("""
<div style="text-align:center;color:#6b7280;font-size:.9rem">
Digital Electronics K-Map Solver • Academic Project • C. V. Raman Global University<br>
Built for learning and demonstrating Boolean-function minimization.
</div>
""", unsafe_allow_html=True)
