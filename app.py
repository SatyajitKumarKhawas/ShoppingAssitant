from agno.agent import Agent
from agno.models.groq import ChatGroq
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.duckduckgo import DuckDuckGoTools
import streamlit as st
from dotenv import load_dotenv
import re
import time

load_dotenv()

# ==================== Global model override ====================
# 🔧 Force ALL agents (including internal ones from tools) to use ChatGroq openai/gpt-oss-20b
Agent.default_model = ChatGroq(model="openai/gpt-oss-20b")

# ==================== Streamlit Page Config & Styles ====================
st.set_page_config(
    page_title="AI Shopping Assistant",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main { padding-top: 2rem; }
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main-header {
        text-align: center; color: white; padding: 2rem 0; margin-bottom: 2rem;
        background: rgba(255,255,255,0.1); border-radius: 15px; backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .feature-card {
        background: rgba(255,255,255,0.95);
        padding: 1.5rem; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem; border-radius: 10px; text-align: center; color: white; margin: 0.5rem 0;
    }
    .success-banner {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem; border-radius: 10px; color: white; margin: 1rem 0; text-align: center;
    }
    .info-box {
        background: rgba(255,255,255,0.9); padding: 1rem; border-radius: 8px;
        border-left: 4px solid #4facfe; margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; border-radius: 25px; padding: 0.5rem 2rem; font-weight: 600;
        transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }
    .stTab { background: rgba(255,255,255,0.95); border-radius: 10px; padding: 1rem; margin: 0.5rem 0; }
    .result-container {
        background: rgba(255,255,255,0.95); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .loading-container { text-align: center; padding: 2rem; background: rgba(255,255,255,0.9); border-radius: 10px; margin: 1rem 0; }
    .footer {
        background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 10px; margin-top: 3rem;
        text-align: center; color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="main-header">
    <h1>🛍️ AI Shopping Assistant</h1>
    <p style="font-size: 1.2rem; margin: 0;">Smart Product Comparison, Reviews & Budget Optimization</p>
    <p style="opacity: 0.8; margin: 0.5rem 0 0 0;">Powered by Advanced AI • Real-time Analysis • Best Deals</p>
</div>
""",
    unsafe_allow_html=True,
)

# ==================== Sidebar ====================
with st.sidebar:
    st.markdown(
        """
    <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.95); border-radius: 10px; margin-bottom: 1rem;">
        <h3 style="color: #667eea; margin: 0;">🎯 Preferences</h3>
    </div>
    """,
        unsafe_allow_html=True,
    )

    currency = st.selectbox("💰 Currency", ["₹ INR", "$ USD", "€ EUR"], index=0)
    region = st.selectbox("🌍 Region", ["India", "USA", "Europe", "Global"], index=0)
    st.markdown("---")
    st.markdown(
        """
    <div class="metric-card">
        <h4>📊 Today's Stats</h4>
        <p>Products Analyzed: <strong>1,247</strong></p>
        <p>Money Saved: <strong>₹45,230</strong></p>
        <p>Happy Customers: <strong>892</strong></p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        """
    <div class="info-box">
        <h4>💡 Pro Tips</h4>
        <ul>
            <li>Compare at least 3 products</li>
            <li>Check reviews thoroughly</li>
            <li>Set a realistic budget</li>
            <li>Consider long-term value</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ==================== Utility helpers ====================

def clamp(text: str, max_chars: int = 6000) -> str:
    text = text or ""
    return (text[:max_chars] + " …[truncated]") if len(text) > max_chars else text


def make_firecrawl_tool(
    max_pages=1,
    max_results=5,
    chunk_chars=2500,
    extract_readable=True,
    include_links=True,
):
    """Create a constrained Firecrawl tool. If your FirecrawlTools version doesn't
    support a param, remove it; the idea is to keep the payloads small.
    """
    try:
        return FirecrawlTools(
            max_pages=max_pages,
            max_results=max_results,
            chunk_chars=chunk_chars,
            extract_readable=extract_readable,
            include_links=include_links,
        )
    except TypeError:
        # Fallback: minimal init if some args aren't supported in your version
        return FirecrawlTools()


def get_candidate_urls(query: str, k: int = 5):
    """Use DuckDuckGo to fetch a few URLs first, so Firecrawl only scrapes those."""
    ddg_agent = Agent(
        name="Search",
        model=ChatGroq(model="openai/gpt-oss-20b"),
        tools=[DuckDuckGoTools()],
    )
    res = ddg_agent.run(
        f"Give top {k} shopping result URLs for: {query}. Only list URLs, one per line."
    )
    urls = re.findall(r"https?://\S+", (res.content or ""))
    return urls[:k]

# ==================== Feature functions (overflow-safe) ====================

def get_product_recommendations(
    shopping_list: str, budget: int, priority: str = "Best Value"
):
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("🔍 Initializing product research...")
        progress_bar.progress(20)

        # Pre-filter URLs
        status_text.text("🌐 Searching candidate listings...")
        candidate_query = f"{shopping_list} site:amazon.in OR site:flipkart.com"
        urls = get_candidate_urls(candidate_query, k=5)

        progress_bar.progress(45)
        status_text.text("🛒 Scraping selected pages...")

        agent = Agent(
            name="Product Research Agent",
            model=ChatGroq(model="openai/gpt-oss-20b"),
            instructions=[
                "You find the best products within the user's budget.",
                "Analyze ONLY the URLs provided. Ignore other sources.",
                "Return at most 5 products TOTAL across all sites.",
                "Per product (single compact block): Name | Price | 3 key features | Source URL.",
                "No raw HTML, no long quotes, no full review dumps.",
                f"Optimization priority: {priority}.",
                "End with: Total estimated cost and whether it's within budget.",
            ],
            tools=[
                make_firecrawl_tool(
                    max_pages=1, max_results=len(urls) or 5, chunk_chars=2500
                )
            ],
            markdown=True,
        )

        query = (
            "Analyze ONLY these URLs:\n"
            + ("\n".join(urls) if urls else "None found; rely on minimal search.")
            + f"\n\nShopping List: {shopping_list}\nBudget: ₹{budget}\nPriority: {priority}\n"
            + "Sites: prefer Amazon India and Flipkart. Keep output concise and structured."
        )

        progress_bar.progress(70)
        status_text.text("🧠 Analyzing options...")
        output = agent.run(query)

        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        time.sleep(0.8)
        progress_bar.empty()
        status_text.empty()

        return output.content
    except Exception as e:
        return f"Error in product research: {str(e)}"


def analyze_sentiment(product_url: str):
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("🔍 Accessing product page...")
        progress_bar.progress(25)

        agent = Agent(
            name="Review Sentiment Agent",
            model=ChatGroq(model="openai/gpt-oss-20b"),
            instructions=[
                "You are a sentiment analysis expert.",
                "Extract short snippets of user reviews using Firecrawl.",
                "Classify each as Positive / Negative / Neutral.",
                "Report counts and percentages for each sentiment.",
                "List top 3 pros and top 3 cons in short bullets.",
                "Conclude with a one-line verdict: Buy / Consider / Avoid.",
                "Do NOT paste long raw review text. Keep everything brief.",
                "Analyze at most 10 reviews if available.",
            ],
            tools=[make_firecrawl_tool(max_pages=1, max_results=1, chunk_chars=2000)],
            markdown=True,
        )

        query = (
            f"Analyze user reviews from: {product_url}\n"
            "Extract up to 10 concise snippets. Keep output compact and tabular/bulleted."
        )

        status_text.text("📝 Extracting reviews...")
        progress_bar.progress(55)
        output = agent.run(query)

        status_text.text("✅ Analysis complete!")
        progress_bar.progress(100)
        time.sleep(0.6)
        progress_bar.empty()
        status_text.empty()

        return output.content
    except Exception as e:
        return f"Error in sentiment analysis: {str(e)}"


def teach_before_buy(product_type: str):
    try:
        agent = Agent(
            name="Buyer Educator",
            model=ChatGroq(model="openai/gpt-oss-20b"),
            instructions=[
                "Explain what to look for in the product type.",
                "Use short sections: Key Specs, Nice-to-Haves, Budget Tiers, Mistakes to Avoid, Quick Checklist.",
                "Keep it concise and practical. No fluff.",
            ],
            markdown=True,
        )
        query = (
            f"Buying a {product_type}: provide the sections requested, keep bullets short."
        )
        output = agent.run(query)
        return output.content
    except Exception as e:
        return f"Error: {str(e)}"


def compare_product(product_name: str):
    try:
        # Pre-filter URLs for the exact product name
        urls = get_candidate_urls(
            f'"{product_name}" site:amazon.in OR site:flipkart.com OR site:reliancedigital.in',
            k=5,
        )

        agent = Agent(
            name="Product Comparison Agent",
            model=ChatGroq(model="openai/gpt-oss-20b"),
            instructions=[
                "Compare products across the provided URLs.",
                "Return at most 5 variants total.",
                "Per product: Name | Price | Key differentiators (3 bullets) | Source URL.",
                "End with: Best pick and 1-sentence rationale.",
                "No long quotes, specs tables should be compact.",
            ],
            tools=[
                make_firecrawl_tool(
                    max_pages=1, max_results=len(urls) or 5, chunk_chars=2500
                )
            ],
            markdown=True,
        )

        query = (
            "Compare ONLY these links (ignore others):\n"
            + ("\n".join(urls) if urls else "None found; compare top known variants briefly.")
            + f"\n\nTarget product: {product_name}\nKeep output compact."
        )

        output = agent.run(query)
        return output.content
    except Exception as e:
        return f"Error: {str(e)}"


def get_trending_products():
    try:
        agent = Agent(
            name="Trending Product Finder",
            model=ChatGroq(model="openai/gpt-oss-20b"),
            instructions=[
                "Find trending products under ₹1000 from major e-commerce sites.",
                "Return at most 8 items. Keep each item to one line: Name | Typical Price | 2 key points | Source URL.",
                "Prefer recent deals pages; avoid long descriptions.",
            ],
            tools=[make_firecrawl_tool(max_pages=1, max_results=8, chunk_chars=2000)],
            markdown=True,
        )
        query = "Trending under ₹1000 in India across Amazon/Flipkart/others. Keep concise."
        output = agent.run(query)
        return output.content
    except Exception as e:
        return f"Error: {str(e)}"

# ==================== Tabs & UI ====================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💼 Budget Optimizer",
        "📊 Review Analysis",
        "🧑‍🎓 Buying Guide",
        "🔍 Compare Products",
        "🌟 Trending Products",
    ]
)

# ---- Tab 1: Budget Optimizer ----
with tab1:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("## 💼 Smart Budget Optimizer")
    st.markdown(
        "Get the best product combinations within your budget with AI-powered recommendations."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        shopping_list = st.text_area(
            "🛍️ Shopping List",
            "wireless headphones, ergonomic mouse, laptop backpack",
            height=120,
            help="Enter products separated by commas",
        )
    with col2:
        budget = st.number_input(
            "💰 Budget (₹)",
            min_value=500,
            max_value=500000,
            value=15000,
            step=500,
            help="Set your maximum budget",
        )
        priority = st.selectbox(
            "🎯 Priority",
            ["Best Value", "Premium Quality", "Budget Conscious", "Latest Technology"],
            help="Choose your optimization strategy",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        optimize_button = st.button("🚀 Optimize My Shopping", use_container_width=True)

    if optimize_button:
        if not shopping_list.strip():
            st.error("⚠️ Please enter your shopping list")
        else:
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            products_result = get_product_recommendations(
                shopping_list, budget, priority
            )
            st.markdown('<div class="success-banner">', unsafe_allow_html=True)
            st.markdown("### ✅ Optimization Complete!")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("### 📋 Product Recommendations")
            st.markdown(clamp(products_result, 6000))
            st.markdown("</div>", unsafe_allow_html=True)

# ---- Tab 2: Review Analysis ----
with tab2:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("## 📊 Advanced Review Analysis")
    st.markdown(
        "Get detailed sentiment analysis and insights from customer reviews."
    )
    product_url = st.text_input(
        "🔗 Product Page URL",
        placeholder="https://amazon.in/product-page",
        help="Paste the product URL from any e-commerce site",
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze Reviews", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if analyze_button:
        if not product_url:
            st.error("⚠️ Please enter a valid product URL")
        else:
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            result = analyze_sentiment(product_url)
            st.markdown('<div class="success-banner">', unsafe_allow_html=True)
            st.markdown("### 📊 Review Analysis Results")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(clamp(result, 6000))
            st.markdown("</div>", unsafe_allow_html=True)

# ---- Tab 3: Buying Guide ----
with tab3:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("## 🧑‍🎓 Smart Buying Guide")
    st.markdown(
        "Learn what to look for before making a purchase with expert guidance."
    )
    product_type = st.text_input(
        "🏷️ Product Type",
        placeholder="e.g., Smartwatch, Laptop, Camera",
        help="Enter the type of product you want to buy",
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        guide_button = st.button("📚 Get Buying Guide", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if guide_button:
        if not product_type.strip():
            st.error("⚠️ Please enter a product type")
        else:
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            result = teach_before_buy(product_type)
            st.markdown('<div class="success-banner">', unsafe_allow_html=True)
            st.markdown(f"### 📖 Buying Guide: {product_type}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(clamp(result, 6000))
            st.markdown("</div>", unsafe_allow_html=True)

# ---- Tab 4: Compare Products ----
with tab4:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("## 🔍 Product Comparison")
    st.markdown(
        "Compare products across multiple platforms to find the best deal."
    )
    product_name = st.text_input(
        "📱 Product Name",
        placeholder="e.g., iPhone 15 Pro, Samsung Galaxy S24",
        help="Enter the specific product you want to compare",
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        compare_button = st.button("⚖️ Compare Products", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if compare_button:
        if not product_name.strip():
            st.error("⚠️ Please enter a product name")
        else:
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            result = compare_product(product_name)
            st.markdown('<div class="success-banner">', unsafe_allow_html=True)
            st.markdown("### 📊 Product Comparison Results")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(clamp(result, 6000))
            st.markdown("</div>", unsafe_allow_html=True)

# ---- Tab 5: Trending Products ----
with tab5:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("## 🌟 Trending Products")
    st.markdown(
        "Discover the hottest products and best deals available right now."
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        trending_button = st.button(
            "🔥 Get Trending Products", use_container_width=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    if trending_button:
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        result = get_trending_products()
        st.markdown('<div class="success-banner">', unsafe_allow_html=True)
        st.markdown("### 🔥 Trending Products")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(clamp(result, 6000))
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== Footer ====================

st.markdown(
    """
<div class="footer">
    <h3>🛍️ AI Shopping Assistant</h3>
    <p>Built with ❤️ by Satyajit | Powered by ChatGroq & Firecrawl | Enhanced with Streamlit</p>
    <p>🔒 Secure • 🚀 Fast • 🎯 Accurate • 💡 Smart</p>
    <div style="margin-top: 1rem;">
        <span style="margin: 0 1rem;">📧 Contact</span>
        <span style="margin: 0 1rem;">🐛 Report Bug</span>
        <span style="margin: 0 1rem;">⭐ Rate Us</span>
        <span style="margin: 0 1rem;">📖 Documentation</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)
