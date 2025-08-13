"""
AI-Powered Scrapy Dashboard - Streamlit Application
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import time

# Import our modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db, init_database
from database.models import Product, AIEnrichment, Source, PriceHistory
from ai_engine.categorizer import get_categorizer
from ai_engine.description_generator import get_description_generator
from config.settings import DASHBOARD_CONFIG, PRODUCT_CATEGORIES

# Configure Streamlit page
st.set_page_config(
    page_title=DASHBOARD_CONFIG['title'],
    page_icon=DASHBOARD_CONFIG['page_icon'],
    layout=DASHBOARD_CONFIG['layout'],
    initial_sidebar_state=DASHBOARD_CONFIG['initial_sidebar_state']
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-success { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-error { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False

if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'Overview'

# Database initialization
def initialize_database():
    """Initialize database connection"""
    try:
        if not st.session_state.db_initialized:
            with st.spinner("Initializing database..."):
                success = init_database()
                if success:
                    st.session_state.db_initialized = True
                    st.success("Database initialized successfully!")
                else:
                    st.error("Database initialization failed!")
                    return False
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# Initialize database
if not initialize_database():
    st.error("Failed to initialize database. Please check your configuration.")
    st.stop()

# Get database manager
db_manager = get_db()

# Main dashboard
def main_dashboard():
    """Main dashboard application"""
    
    # Header
    st.markdown(f'<h1 class="main-header">{DASHBOARD_CONFIG["title"]}</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    tabs = ["Overview", "Products", "AI Insights", "Scraping", "Analytics", "Settings"]
    
    current_tab = st.sidebar.selectbox("Select Tab", tabs, index=tabs.index(st.session_state.current_tab))
    st.session_state.current_tab = current_tab
    
    # Tab content
    if current_tab == "Overview":
        show_overview_tab()
    elif current_tab == "Products":
        show_products_tab()
    elif current_tab == "AI Insights":
        show_ai_insights_tab()
    elif current_tab == "Scraping":
        show_scraping_tab()
    elif current_tab == "Analytics":
        show_analytics_tab()
    elif current_tab == "Settings":
        show_settings_tab()

def show_overview_tab():
    """Show overview dashboard"""
    st.header("📊 Dashboard Overview")
    
    # Get database stats
    try:
        stats = db_manager.get_database_stats()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Products", stats.get('total_products', 0))
        
        with col2:
            st.metric("Total Sources", stats.get('total_sources', 0))
        
        with col3:
            st.metric("AI Enriched", stats.get('products_with_ai', 0))
        
        with col4:
            st.metric("Recent Scrapes", stats.get('recent_scrapes', 0))
        
        # Database connection status
        st.subheader("🔌 System Status")
        conn_info = db_manager.get_connection_info()
        
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            st.write("**Database Connection:**")
            if conn_info['connected']:
                st.success("✅ Connected")
            else:
                st.error("❌ Disconnected")
            
            st.write(f"**Host:** {conn_info['host']}")
            st.write(f"**Database:** {conn_info['database']}")
        
        with status_col2:
            st.write("**Connection Pool:**")
            st.write(f"**Pool Size:** {conn_info['pool_size'] or 'N/A'}")
            st.write(f"**Checked Out:** {conn_info['checked_out'] or 'N/A'}")
        
        # Recent activity
        st.subheader("📈 Recent Activity")
        
        # Get recent products
        with db_manager.get_session() as session:
            recent_products = session.query(Product).order_by(Product.scraped_at.desc()).limit(5).all()
            
            if recent_products:
                recent_data = []
                for product in recent_products:
                    recent_data.append({
                        'Title': product.title[:50] + '...' if len(product.title) > 50 else product.title,
                        'Price': f"${product.price:.2f}" if product.price else 'N/A',
                        'Source': product.source.name if product.source else 'Unknown',
                        'Scraped': product.scraped_at.strftime('%Y-%m-%d %H:%M') if product.scraped_at else 'N/A'
                    })
                
                df = pd.DataFrame(recent_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No recent products found")
        
    except Exception as e:
        st.error(f"Error loading overview data: {e}")

def show_products_tab():
    """Show products management tab"""
    st.header("📦 Product Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.selectbox("Category", ["All"] + PRODUCT_CATEGORIES)
    
    with col2:
        price_range = st.slider("Price Range ($)", 0, 1000, (0, 1000))
    
    with col3:
        source_filter = st.selectbox("Source", ["All"])
        # Populate sources
        try:
            with db_manager.get_session() as session:
                sources = session.query(Source).all()
                source_names = ["All"] + [source.name for source in sources]
                source_filter = st.selectbox("Source", source_names)
        except:
            pass
    
    # Search
    search_query = st.text_input("Search products", placeholder="Enter product title...")
    
    # Load products
    try:
        with db_manager.get_session() as session:
            query = session.query(Product)
            
            # Apply filters
            if category_filter != "All":
                query = query.join(AIEnrichment).filter(AIEnrichment.category == category_filter)
            
            if price_range[0] > 0:
                query = query.filter(Product.price >= price_range[0])
            if price_range[1] < 1000:
                query = query.filter(Product.price <= price_range[1])
            
            if search_query:
                query = query.filter(Product.title.ilike(f"%{search_query}%"))
            
            products = query.limit(100).all()
            
            if products:
                # Convert to DataFrame
                product_data = []
                for product in products:
                    # Get AI enrichment if available
                    enrichment = session.query(AIEnrichment).filter(
                        AIEnrichment.product_id == product.id
                    ).first()
                    
                    product_data.append({
                        'ID': product.id,
                        'Title': product.title,
                        'Price': f"${product.price:.2f}" if product.price else 'N/A',
                        'Category': enrichment.category if enrichment else 'Not Categorized',
                        'Source': product.source.name if product.source else 'Unknown',
                        'Rating': f"{product.rating:.1f}" if product.rating else 'N/A',
                        'Scraped': product.scraped_at.strftime('%Y-%m-%d') if product.scraped_at else 'N/A'
                    })
                
                df = pd.DataFrame(product_data)
                st.dataframe(df, use_container_width=True)
                
                # Product details on selection
                st.subheader("🔍 Product Details")
                selected_id = st.selectbox("Select Product ID", [p['ID'] for p in product_data])
                
                if selected_id:
                    selected_product = session.query(Product).filter(Product.id == selected_id).first()
                    if selected_product:
                        show_product_details(selected_product, session)
            else:
                st.info("No products found matching the criteria")
                
    except Exception as e:
        st.error(f"Error loading products: {e}")

def show_product_details(product, session):
    """Show detailed information for a selected product"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Title:** {product.title}")
        st.write(f"**Price:** ${product.price:.2f}" if product.price else "**Price:** N/A")
        st.write(f"**Currency:** {product.currency}")
        st.write(f"**Source:** {product.source.name if product.source else 'Unknown'}")
        st.write(f"**Scraped:** {product.scraped_at.strftime('%Y-%m-%d %H:%M') if product.scraped_at else 'N/A'}")
        
        if product.image_url:
            st.image(product.image_url, caption="Product Image", use_column_width=True)
    
    with col2:
        # Get AI enrichment
        enrichment = session.query(AIEnrichment).filter(
            AIEnrichment.product_id == product.id
        ).first()
        
        if enrichment:
            st.write(f"**AI Category:** {enrichment.category}")
            st.write(f"**Confidence:** {enrichment.confidence_score:.2f}" if enrichment.confidence_score else "**Confidence:** N/A")
            
            if enrichment.ai_description:
                st.write("**AI Description:**")
                st.write(enrichment.ai_description)
            
            if enrichment.ai_tags:
                try:
                    tags = json.loads(enrichment.ai_tags)
                    st.write(f"**AI Tags:** {', '.join(tags)}")
                except:
                    pass
        else:
            st.info("No AI enrichment available")
        
        # Price history
        price_history = session.query(PriceHistory).filter(
            PriceHistory.product_id == product.id
        ).order_by(PriceHistory.recorded_at.desc()).limit(10).all()
        
        if price_history:
            st.write("**Price History:**")
            for ph in price_history:
                st.write(f"{ph.recorded_at.strftime('%Y-%m-%d')}: ${ph.price:.2f}")

def show_ai_insights_tab():
    """Show AI insights and analysis"""
    st.header("🧠 AI Insights & Analysis")
    
    # AI Engine Status
    st.subheader("🤖 AI Engine Status")
    
    try:
        from ai_engine.langchain_chain import get_ai_engine
        ai_engine = get_ai_engine()
        
        if ai_engine.llm:
            st.success("✅ AI Engine: Active (OpenRouter)")
            st.write(f"**Model:** {ai_engine.llm.model_name}")
        else:
            st.warning("⚠️ AI Engine: Mock Mode (No API Key)")
            st.write("**Status:** Running with fallback categorization")
        
        # AI Processing Stats
        st.subheader("📊 AI Processing Statistics")
        
        categorizer = get_categorizer()
        desc_generator = get_description_generator()
        
        col1, col2 = st.columns(2)
        
        with col1:
            cat_stats = categorizer.get_categorization_stats()
            st.write("**Categorization:**")
            st.write(f"• Total Products: {cat_stats.get('total_products', 0)}")
            st.write(f"• Categorized: {cat_stats.get('categorized_products', 0)}")
            st.write(f"• Rate: {cat_stats.get('categorization_rate', 0):.1f}%")
        
        with col2:
            desc_stats = desc_generator.get_description_stats()
            st.write("**Description Generation:**")
            st.write(f"• Enriched Products: {desc_stats.get('total_enriched_products', 0)}")
            st.write(f"• With Descriptions: {desc_stats.get('products_with_descriptions', 0)}")
            st.write(f"• Rate: {desc_stats.get('description_generation_rate', 0):.1f}%")
        
        # Category Distribution
        if cat_stats.get('category_distribution'):
            st.subheader("📈 Category Distribution")
            
            categories = list(cat_stats['category_distribution'].keys())
            counts = list(cat_stats['category_distribution'].values())
            
            fig = px.bar(
                x=categories, 
                y=counts,
                title="Products by Category",
                labels={'x': 'Category', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # AI Actions
        st.subheader("⚡ AI Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Run Categorization", type="primary"):
                with st.spinner("Running AI categorization..."):
                    result = categorizer.categorize_products(limit=50)
                    if result['status'] == 'success':
                        st.success(f"Categorization completed! {result['products_successful']} products processed")
                    else:
                        st.error(f"Categorization failed: {result.get('message', 'Unknown error')}")
        
        with col2:
            if st.button("✍️ Generate Descriptions", type="primary"):
                with st.spinner("Generating AI descriptions..."):
                    result = desc_generator.generate_descriptions(limit=50)
                    if result['status'] == 'success':
                        st.success(f"Description generation completed! {result['products_successful']} products processed")
                    else:
                        st.error(f"Description generation failed: {result.get('message', 'Unknown error')}")
        
        # Recent AI Processing
        st.subheader("📝 Recent AI Processing")
        
        try:
            with db_manager.get_session() as session:
                recent_logs = session.query(AIProcessingLog).order_by(
                    AIProcessingLog.processed_at.desc()
                ).limit(10).all()
                
                if recent_logs:
                    log_data = []
                    for log in recent_logs:
                        log_data.append({
                            'Product ID': log.product_id,
                            'Operation': log.operation_type.title(),
                            'Status': '✅ Success' if log.success else '❌ Failed',
                            'Model': log.model_used or 'N/A',
                            'Time': log.processed_at.strftime('%Y-%m-%d %H:%M') if log.processed_at else 'N/A'
                        })
                    
                    df = pd.DataFrame(log_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No recent AI processing logs found")
                    
        except Exception as e:
            st.error(f"Error loading AI logs: {e}")
            
    except Exception as e:
        st.error(f"Error loading AI insights: {e}")

def show_scraping_tab():
    """Show scraping management tab"""
    st.header("🕷️ Scraping Management")
    
    # Scraping Status
    st.subheader("📊 Scraping Status")
    
    try:
        with db_manager.get_session() as session:
            sources = session.query(Source).all()
            
            if sources:
                source_data = []
                for source in sources:
                    # Get recent scraping info
                    recent_products = session.query(Product).filter(
                        Product.source_id == source.id
                    ).order_by(Product.scraped_at.desc()).first()
                    
                    source_data.append({
                        'Name': source.name,
                        'URL': source.base_url,
                        'Type': source.type,
                        'Status': '✅ Enabled' if source.enabled else '❌ Disabled',
                        'Last Scraped': recent_products.scraped_at.strftime('%Y-%m-%d %H:%M') if recent_products and recent_products.scraped_at else 'Never',
                        'Products': session.query(Product).filter(Product.source_id == source.id).count()
                    })
                
                df = pd.DataFrame(source_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No sources configured")
        
        # Manual Scraping
        st.subheader("🔧 Manual Scraping")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📚 Scrape Books Site", type="primary"):
                st.info("This would run the Scrapy spider for books.toscrape.com")
                # In a real implementation, this would trigger the spider
        
        with col2:
            if st.button("💬 Scrape Quotes Site", type="primary"):
                st.info("This would run the Scrapy spider for quotes.toscrape.com")
                # In a real implementation, this would trigger the spider
        
        # Scraping Configuration
        st.subheader("⚙️ Scraping Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Scraping Settings:**")
            st.write("• Delay between requests: 2 seconds")
            st.write("• User agent: Custom browser")
            st.write("• Retry attempts: 3")
        
        with col2:
            st.write("**Scheduling:**")
            st.write("• Frequency: Daily")
            st.write("• Time: 2:00 AM")
            st.write("• Auto-cleanup: 30 days")
        
    except Exception as e:
        st.error(f"Error loading scraping data: {e}")

def show_analytics_tab():
    """Show analytics and reporting tab"""
    st.header("📊 Analytics & Reporting")
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Analytics Overview
    st.subheader("📈 Analytics Overview")
    
    try:
        with db_manager.get_session() as session:
            # Price trends
            st.write("**Price Trends**")
            
            # Get price history data
            price_data = session.query(PriceHistory).filter(
                PriceHistory.recorded_at >= start_date,
                PriceHistory.recorded_at <= end_date
            ).all()
            
            if price_data:
                # Group by date and calculate average price
                price_df = pd.DataFrame([
                    {
                        'date': ph.recorded_at.date(),
                        'price': ph.price
                    }
                    for ph in price_data
                ])
                
                if not price_df.empty:
                    daily_avg = price_df.groupby('date')['price'].mean().reset_index()
                    
                    fig = px.line(
                        daily_avg, 
                        x='date', 
                        y='price',
                        title="Average Daily Price Trend",
                        labels={'date': 'Date', 'price': 'Average Price ($)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No price data available for selected date range")
            else:
                st.info("No price history data available")
            
            # Category performance
            st.write("**Category Performance**")
            
            category_data = session.query(
                AIEnrichment.category,
                session.query(Product).join(AIEnrichment).filter(
                    AIEnrichment.category == AIEnrichment.category
                ).count().label('count')
            ).group_by(AIEnrichment.category).all()
            
            if category_data:
                categories = [cat for cat, _ in category_data]
                counts = [count for _, count in category_data]
                
                fig = px.pie(
                    values=counts,
                    names=categories,
                    title="Products by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Source performance
            st.write("**Source Performance**")
            
            source_data = session.query(
                Source.name,
                session.query(Product).filter(Product.source_id == Source.id).count().label('count')
            ).group_by(Source.name).all()
            
            if source_data:
                sources = [source for source, _ in source_data]
                counts = [count for _, count in source_data]
                
                fig = px.bar(
                    x=sources,
                    y=counts,
                    title="Products by Source",
                    labels={'x': 'Source', 'y': 'Product Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Export options
        st.subheader("📤 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Products (CSV)"):
                st.info("This would export all products to CSV")
                # In a real implementation, this would generate and download a CSV file
        
        with col2:
            if st.button("Export AI Data (JSON)"):
                st.info("This would export AI enrichment data to JSON")
                # In a real implementation, this would generate and download a JSON file
                
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")

def show_settings_tab():
    """Show settings and configuration tab"""
    st.header("⚙️ Settings & Configuration")
    
    # Database Settings
    st.subheader("🗄️ Database Settings")
    
    try:
        conn_info = db_manager.get_connection_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Connection Details:**")
            st.write(f"Host: {conn_info['host']}")
            st.write(f"Port: {conn_info['port']}")
            st.write(f"Database: {conn_info['database']}")
            st.write(f"User: {conn_info['user']}")
        
        with col2:
            st.write("**Status:**")
            if conn_info['connected']:
                st.success("✅ Connected")
            else:
                st.error("❌ Disconnected")
            
            st.write(f"Pool Size: {conn_info['pool_size'] or 'N/A'}")
            st.write(f"Checked Out: {conn_info['checked_out'] or 'N/A'}")
        
        # Test connection
        if st.button("🔍 Test Connection"):
            if db_manager.test_connection():
                st.success("Database connection successful!")
            else:
                st.error("Database connection failed!")
        
        # AI Settings
        st.subheader("🤖 AI Configuration")
        
        try:
            from config.settings import OPENROUTER_CONFIG
            
            st.write("**OpenRouter Configuration:**")
            st.write(f"Model: {OPENROUTER_CONFIG['model']}")
            st.write(f"Max Tokens: {OPENROUTER_CONFIG['max_tokens']}")
            st.write(f"Temperature: {OPENROUTER_CONFIG['temperature']}")
            
            # API Key status
            if OPENROUTER_CONFIG['api_key']:
                st.success("✅ API Key configured")
            else:
                st.warning("⚠️ No API Key configured - running in mock mode")
                
        except Exception as e:
            st.error(f"Error loading AI configuration: {e}")
        
        # System Actions
        st.subheader("🔄 System Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clean Old Data", type="secondary"):
                with st.spinner("Cleaning old data..."):
                    try:
                        db_manager.cleanup_old_data(days_to_keep=30)
                        st.success("Data cleanup completed!")
                    except Exception as e:
                        st.error(f"Data cleanup failed: {e}")
        
        with col2:
            if st.button("🔄 Reset Database", type="secondary"):
                if st.checkbox("I understand this will delete all data"):
                    if st.button("⚠️ Confirm Reset", type="primary"):
                        st.error("This action is not implemented in the demo")
                        # In production, this would reset the database
        
        # Logs
        st.subheader("📝 System Logs")
        
        # This would show recent system logs
        st.info("System logs would be displayed here in a production environment")
        
    except Exception as e:
        st.error(f"Error loading settings: {e}")

# Run the dashboard
if __name__ == "__main__":
    main_dashboard() 