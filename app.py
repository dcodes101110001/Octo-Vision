"""
Octo-Vision: Paste Site Scraper with Keyword Detection
A Streamlit application for scraping paste sites and scanning for keyword patterns
"""

import streamlit as st
import pandas as pd
from scraper import PasteScraper
from scanner import KeywordScanner

# Page configuration
st.set_page_config(
    page_title="Octo-Vision - Paste Site Scraper",
    page_icon="🔍",
    layout="wide"
)

# Title and description
st.title("🔍 Octo-Vision: Paste Site Scraper")
st.markdown("""
Scrape paste sites like Pastebin and scan for specific keyword patterns.
Upload a CSV file with keywords or enter them manually.
""")

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

# Initialize session state
if 'scanner' not in st.session_state:
    st.session_state.scanner = KeywordScanner()
if 'scraper' not in st.session_state:
    st.session_state.scraper = PasteScraper()
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = []

# Keyword input options
st.sidebar.subheader("🔑 Keyword Setup")
keyword_method = st.sidebar.radio(
    "Choose keyword input method:",
    ["Upload CSV", "Manual Entry"]
)

keywords = []

if keyword_method == "Upload CSV":
    st.sidebar.markdown("**Upload a CSV file with keywords**")
    st.sidebar.markdown("*Format: One keyword per line in the first column*")
    
    uploaded_file = st.sidebar.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file with keywords in the first column"
    )
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.getvalue().decode('utf-8')
            keywords = st.session_state.scanner.load_keywords_from_csv(content)
            st.sidebar.success(f"✅ Loaded {len(keywords)} keywords from CSV")
            
            with st.sidebar.expander("View loaded keywords"):
                st.write(keywords)
        except Exception as e:
            st.sidebar.error(f"❌ Error loading CSV: {e}")

else:  # Manual Entry
    st.sidebar.markdown("**Enter keywords manually**")
    keyword_input = st.sidebar.text_area(
        "Keywords (one per line)",
        height=150,
        placeholder="password\napi_key\nsecret\ncredit card\nSSN\nemail"
    )
    
    if keyword_input:
        keywords = [k.strip() for k in keyword_input.split('\n') if k.strip()]
        st.session_state.scanner.load_keywords_from_list(keywords)
        st.sidebar.info(f"📝 {len(keywords)} keywords entered")

# Scanner options
st.sidebar.subheader("🔍 Scanner Options")
case_sensitive = st.sidebar.checkbox("Case sensitive search", value=False)
st.session_state.scanner.case_sensitive = case_sensitive

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📥 Scrape Pastes")
    
    scrape_method = st.radio(
        "Select scraping method:",
        ["Recent Pastebin Posts", "Custom URL"]
    )
    
    if scrape_method == "Recent Pastebin Posts":
        num_pastes = st.slider(
            "Number of recent pastes to scrape",
            min_value=1,
            max_value=20,
            value=10,
            help="Note: Scraping may take time due to rate limiting"
        )
        
        if st.button("🚀 Start Scraping", type="primary"):
            if not keywords:
                st.warning("⚠️ Please add keywords first!")
            else:
                # Create progress bar and status text
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text(f"Scraping {num_pastes} recent pastes from Pastebin...")
                    progress_bar.progress(10)
                    
                    pastes = st.session_state.scraper.scrape_pastebin_recent(limit=num_pastes)
                    
                    if pastes:
                        progress_bar.progress(60)
                        status_text.text(f"✅ Scraped {len(pastes)} pastes. Now scanning for keywords...")
                        
                        results = st.session_state.scanner.scan_multiple_texts(pastes)
                        st.session_state.scan_results = results
                        
                        progress_bar.progress(100)
                        status_text.empty()
                        progress_bar.empty()
                        
                        if results:
                            st.success(f"🎯 Found matches in {len(results)} paste(s)!")
                        else:
                            st.info("ℹ️ No keyword matches found")
                    else:
                        progress_bar.empty()
                        status_text.empty()
                        st.error("❌ Failed to scrape pastes. Please try again later.")
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ Error during scraping: {str(e)}")
    
    else:  # Custom URL
        custom_url = st.text_input(
            "Enter paste URL",
            placeholder="https://pastebin.com/xxxxx or https://pastebin.com/raw/xxxxx"
        )
        
        if st.button("🔍 Scan URL", type="primary"):
            if not keywords:
                st.warning("⚠️ Please add keywords first!")
            elif not custom_url:
                st.warning("⚠️ Please enter a URL!")
            else:
                with st.spinner("Scraping URL..."):
                    paste = st.session_state.scraper.scrape_custom_paste(custom_url)
                    
                    if 'error' in paste:
                        st.error(f"❌ Error: {paste['error']}")
                    elif paste.get('content'):
                        with st.spinner("Scanning for keywords..."):
                            scan_result = st.session_state.scanner.scan_text(paste['content'])
                            
                            if scan_result['matches_found']:
                                paste_with_results = {**paste, **scan_result}
                                st.session_state.scan_results = [paste_with_results]
                                st.success(f"🎯 Found {scan_result['match_count']} keyword(s) with {scan_result['total_occurrences']} total occurrence(s)!")
                            else:
                                st.info("ℹ️ No keyword matches found")
                                st.session_state.scan_results = []
                    else:
                        st.error("❌ Could not retrieve content from URL")

with col2:
    st.header("📊 Results")
    
    if st.session_state.scan_results:
        st.markdown(f"**Found {len(st.session_state.scan_results)} paste(s) with keyword matches**")
        
        for idx, result in enumerate(st.session_state.scan_results, 1):
            with st.expander(f"🔍 Match #{idx}: {result.get('title', 'Untitled')}", expanded=(idx == 1)):
                st.markdown(f"**URL:** {result.get('url', 'N/A')}")
                st.markdown(f"**Matched Keywords:** {', '.join(result['matched_keywords'])}")
                st.markdown(f"**Unique Keywords Matched:** {result['match_count']}")
                st.markdown(f"**Total Occurrences:** {result.get('total_occurrences', result['match_count'])}")
                
                st.markdown("**Match Details:**")
                for match_detail in result.get('match_details', [])[:5]:  # Show first 5 matches
                    st.markdown(f"- **{match_detail['keyword']}** at position {match_detail['position']}")
                    st.code(match_detail['context'], language=None)
                
                # Show full content in a collapsed section
                with st.expander("View full paste content"):
                    content = result.get('content', '')
                    content_length = len(content)
                    display_length = min(content_length, 5000)
                    
                    st.caption(f"Content length: {content_length:,} characters")
                    
                    st.text_area(
                        "Content",
                        value=content[:5000],  # Limit to first 5000 chars for display
                        height=300,
                        disabled=True,
                        key=f"content_{idx}"
                    )
                    if content_length > 5000:
                        st.warning(f"⚠️ Content truncated: showing first {display_length:,} of {content_length:,} characters ({(display_length/content_length)*100:.1f}%)")
        
        # Export results
        st.markdown("---")
        st.markdown("**📥 Export Results**")
        st.caption("Note: Content preview in CSV export is limited to 500 characters per paste.")
        if st.button("Export as CSV"):
            # Prepare data for export
            export_data = []
            for result in st.session_state.scan_results:
                content = result.get('content', '')
                export_data.append({
                    'Title': result.get('title', 'Untitled'),
                    'URL': result.get('url', 'N/A'),
                    'Matched Keywords': ', '.join(result['matched_keywords']),
                    'Unique Keywords': result['match_count'],
                    'Total Occurrences': result.get('total_occurrences', result['match_count']),
                    'Content Length': len(content),
                    'Content Preview': content[:500]  # Limited to 500 chars
                })
            
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="octo_vision_results.csv",
                mime="text/csv"
            )
    else:
        st.info("👈 Configure keywords and start scraping to see results here")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📖 Quick Guide
1. **Choose keyword method**: Upload CSV or enter manually
2. **Add keywords**: Upload a CSV file or type keywords
3. **Select scraping method**: Recent posts or custom URL
4. **Start scraping**: Click the button to begin
5. **View results**: Check matches in the Results panel
""")

st.sidebar.markdown("""
### ℹ️ About
**Octo-Vision** helps you monitor paste sites for sensitive information leaks and security concerns.

**Features:**
- 🔍 Scrape recent Pastebin posts
- 🎯 Custom keyword matching
- 📁 CSV keyword upload
- 📊 Detailed match reporting
""")
