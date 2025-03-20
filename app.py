import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
import plotly.express as px
from PIL import Image
import io
import uuid

# Set page configuration
st.set_page_config(
    page_title="Consulting Truck - Gestão de Inventário",
    page_icon="🚚",
    layout="wide"
)

# App state management
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "catalog"

# Constants
CSV_PATH = "data/inventory.csv"
IMAGES_FOLDER = "data/images"

# Ensure directories exist
os.makedirs(IMAGES_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

# Create inventory file if it doesn't exist
if not os.path.exists(CSV_PATH):
    initial_data = pd.DataFrame({
        'truck_id': [],
        'brand': [],
        'model': [],
        'year': [],
        'mileage': [],
        'truck_type': [],
        'transmission': [],
        'engine': [],
        'features': [],
        'condition': [],
        'status': [],
        'price': [],
        'upload_date': [],
        'sale_date': [],
        'sales_person': [],
        'photo_path': []
    })
    initial_data.to_csv(CSV_PATH, index=False)

# Load logo
logo_path = "assets/logo.png"

# Load truck data
@st.cache_data(ttl=60)
def load_data():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame()

# Authentication
def authenticate(username, password):
    # In production, use st.secrets for credentials
    correct_username = st.secrets.get("username", "admin")
    correct_password = st.secrets.get("password", "password")
    
    return username == correct_username and password == correct_password

# Save data to CSV
def save_data(df):
    df.to_csv(CSV_PATH, index=False)

# Save image function
def save_image(image_file, truck_id):
    if image_file is not None:
        # Create a unique filename
        file_extension = os.path.splitext(image_file.name)[1]
        filename = f"{truck_id}{file_extension}"
        filepath = os.path.join(IMAGES_FOLDER, filename)
        
        # Save the image
        with open(filepath, "wb") as f:
            f.write(image_file.getbuffer())
            
        return filepath
    return None

# Generate WhatsApp message with truck details
def generate_whatsapp_message(truck):
    message = f"Olá! Estou interessado no caminhão {truck['brand']} {truck['model']} ({truck['year']}) que vi no catálogo da Consulting Truck. Poderia me fornecer mais informações?"
    encoded_message = base64.urlsafe_b64encode(message.encode()).decode()
    return f"https://wa.me/5541995400112?text={encoded_message}"

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    .logo {
        width: 200px;
    }
    .truck-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .truck-image {
        width: 100%;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .truck-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .truck-details {
        font-size: 0.9rem;
        color: #555;
    }
    .whatsapp-btn {
        background-color: #25D366;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 1rem;
    }
    .header {
        background-color: #FFDA33;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: black;
        text-align: center;
    }
    .filter-container {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .admin-section {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Login form
def login_form():
    st.markdown('<div class="header"><h2>Consulting Truck - Área Administrativa</h2></div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("Credenciais inválidas. Tente novamente.")

# Public catalog view
def public_catalog():
    st.markdown('<div class="logo-container"><img src="https://raw.githubusercontent.com/yourusername/consulting-truck-inventory/main/assets/logo.png" class="logo"></div>', unsafe_allow_html=True)
    st.markdown('<div class="header"><h2>Catálogo de Caminhões - Consulting Truck</h2></div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty or len(df[df['status'] == 'Disponível']) == 0:
        st.info("Não há caminhões disponíveis no momento. Entre em contato conosco para mais informações.")
        
        # Contact information
        st.markdown("""
        ### Entre em Contato
        
        📞 **Telefone:** (41) 99540-0112 - Rapha
        
        📍 **Localização:** Rodovia BR 116 Km 103, Arujá, São José dos Pinhais - PR
        
        🔗 [Instagram @consultruck](https://www.instagram.com/consultruck/)
        
        🔗 [WhatsApp](https://wa.me/5541995400112)
        """)
        return
    
    # Filter only available trucks
    available_trucks = df[df['status'] == 'Disponível'].copy()
    
    # Filters
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        brands = ['Todos'] + sorted(available_trucks['brand'].unique().tolist())
        selected_brand = st.selectbox('Marca', brands)
    
    with col2:
        years = ['Todos'] + sorted(available_trucks['year'].unique().tolist(), reverse=True)
        selected_year = st.selectbox('Ano', years)
        
    with col3:
        types = ['Todos'] + sorted(available_trucks['truck_type'].unique().tolist())
        selected_type = st.selectbox('Tipo', types)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_trucks = available_trucks.copy()
    if selected_brand != 'Todos':
        filtered_trucks = filtered_trucks[filtered_trucks['brand'] == selected_brand]
    if selected_year != 'Todos':
        filtered_trucks = filtered_trucks[filtered_trucks['year'] == selected_year]
    if selected_type != 'Todos':
        filtered_trucks = filtered_trucks[filtered_trucks['truck_type'] == selected_type]
    
    # Display trucks
    if filtered_trucks.empty:
        st.info("Não há caminhões disponíveis com os filtros selecionados.")
    else:
        # Display trucks in a grid
        cols = st.columns(3)
        for i, (_, truck) in enumerate(filtered_trucks.iterrows()):
            col = cols[i % 3]
            
            with col:
                st.markdown('<div class="truck-card">', unsafe_allow_html=True)
                
                # Display image if available
                if pd.notna(truck['photo_path']) and os.path.exists(truck['photo_path']):
                    st.image(truck['photo_path'], use_column_width=True)
                else:
                    st.image("assets/truck_placeholder.png", use_column_width=True)
                
                # Truck information
                st.markdown(f"<div class='truck-title'>{truck['brand']} {truck['model']} ({truck['year']})</div>", unsafe_allow_html=True)
                
                details = f"""
                <div class='truck-details'>
                <strong>Quilometragem:</strong> {truck['mileage']:,.0f} km<br>
                <strong>Motor:</strong> {truck['engine']}<br>
                <strong>Transmissão:</strong> {truck['transmission']}<br>
                <strong>Condição:</strong> {truck['condition']}<br>
                </div>
                """
                st.markdown(details, unsafe_allow_html=True)
                
                # Price if available
                if pd.notna(truck['price']) and truck['price'] > 0:
                    st.markdown(f"<strong>Preço:</strong> R$ {truck['price']:,.2f}".replace(',', '.'), unsafe_allow_html=True)
                
                # WhatsApp button
                whatsapp_url = generate_whatsapp_message(truck)
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📱 Contato via WhatsApp</a>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
    # Contact information at the bottom
    st.markdown("""
    ### Entre em Contato
    
    📞 **Telefone:** (41) 99540-0112 - Rapha
    
    📍 **Localização:** Rodovia BR 116 Km 103, Arujá, São José dos Pinhais - PR
    
    🔗 [Instagram @consultruck](https://www.instagram.com/consultruck/)
    
    🔗 [WhatsApp](https://wa.me/5541995400112)
    """)

# Admin view
def admin_view():
    st.markdown('<div class="header"><h2>Consulting Truck - Gestão de Inventário</h2></div>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Menu")
    views = {
        "catalog": "Ver Catálogo Público",
        "inventory": "Gestão de Inventário",
        "add": "Adicionar Caminhão",
        "analytics": "Análises e Relatórios",
        "settings": "Configurações"
    }
    
    selected_view = st.sidebar.radio("Navegação", list(views.values()))
    
    # Logout button
    if st.sidebar.button("Sair"):
        st.session_state.authenticated = False
        st.experimental_rerun()
    
    # Convert selection back to key
    selected_key = list(views.keys())[list(views.values()).index(selected_view)]
    st.session_state.current_view = selected_key
    
    # Show selected view
    if selected_key == "catalog":
        public_catalog()
    elif selected_key == "inventory":
        inventory_management()
    elif selected_key == "add":
        add_truck()
    elif selected_key == "analytics":
        analytics_view()
    elif selected_key == "settings":
        settings_view()

# Inventory management view
def inventory_management():
    st.markdown('<div class="admin-section"><h3>Gestão de Inventário</h3></div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.info("Não há caminhões no inventário. Adicione seu primeiro caminhão!")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        statuses = ['Todos'] + sorted(df['status'].unique().tolist())
        selected_status = st.selectbox('Status', statuses)
    
    with col2:
        brands = ['Todos'] + sorted(df['brand'].unique().tolist())
        selected_brand = st.selectbox('Marca', brands, key='inv_brand')
        
    with col3:
        years = ['Todos'] + sorted(df['year'].unique().tolist(), reverse=True)
        selected_year = st.selectbox('Ano', years, key='inv_year')
    
    # Apply filters
    filtered_df = df.copy()
    if selected_status != 'Todos':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if selected_brand != 'Todos':
        filtered_df = filtered_df[filtered_df['brand'] == selected_brand]
    if selected_year != 'Todos':
        filtered_df = filtered_df[filtered_df['year'] == selected_year]
    
    # Display inventory
    if filtered_df.empty:
        st.info("Não há caminhões que correspondam aos filtros selecionados.")
    else:
        for _, truck in filtered_df.iterrows():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if pd.notna(truck['photo_path']) and os.path.exists(truck['photo_path']):
                    st.image(truck['photo_path'], width=200)
                else:
                    st.image("assets/truck_placeholder.png", width=200)
            
            with col2:
                st.markdown(f"### {truck['brand']} {truck['model']} ({truck['year']})")
                st.markdown(f"**Status:** {truck['status']}")
                st.markdown(f"**ID:** {truck['truck_id']}")
                
                if pd.notna(truck['price']) and truck['price'] > 0:
                    st.markdown(f"**Preço:** R$ {truck['price']:,.2f}".replace(',', '.'))
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"Editar", key=f"edit_{truck['truck_id']}"):
                        st.session_state.edit_truck_id = truck['truck_id']
                        st.session_state.current_view = "add"
                        st.experimental_rerun()
                
                with col2:
                    if truck['status'] == 'Disponível':
                        if st.button(f"Marcar como Vendido", key=f"sold_{truck['truck_id']}"):
                            # Update status
                            df.loc[df['truck_id'] == truck['truck_id'], 'status'] = 'Vendido'
                            df.loc[df['truck_id'] == truck['truck_id'], 'sale_date'] = datetime.now().strftime("%Y-%m-%d")
                            save_data(df)
                            st.success("Caminhão marcado como vendido!")
                            st.experimental_rerun()
                    else:
                        if st.button(f"Marcar como Disponível", key=f"avail_{truck['truck_id']}"):
                            # Update status
                            df.loc[df['truck_id'] == truck['truck_id'], 'status'] = 'Disponível'
                            df.loc[df['truck_id'] == truck['truck_id'], 'sale_date'] = None
                            save_data(df)
                            st.success("Caminhão marcado como disponível!")
                            st.experimental_rerun()
                
                with col3:
                    if st.button(f"Excluir", key=f"delete_{truck['truck_id']}"):
                        # Delete confirmation
                        st.session_state.delete_truck_id = truck['truck_id']
                        st.session_state.show_delete_confirmation = True
            
            st.markdown("---")
    
    # Handle delete confirmation
    if hasattr(st.session_state, 'show_delete_confirmation') and st.session_state.show_delete_confirmation:
        st.warning(f"Tem certeza que deseja excluir este caminhão? Esta ação não pode ser desfeita.")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Sim, excluir"):
                # Delete truck
                truck_id = st.session_state.delete_truck_id
                
                # Get photo path to delete
                photo_path = df.loc[df['truck_id'] == truck_id, 'photo_path'].values[0]
                
                # Remove from dataframe
                df = df[df['truck_id'] != truck_id]
                save_data(df)
                
                # Delete photo if it exists
                if pd.notna(photo_path) and os.path.exists(photo_path):
                    os.remove(photo_path)
                
                st.success("Caminhão excluído com sucesso!")
                
                # Reset state
                del st.session_state.show_delete_confirmation
                del st.session_state.delete_truck_id
                
                st.experimental_rerun()
        
        with col2:
            if st.button("Cancelar"):
                # Reset state
                del st.session_state.show_delete_confirmation
                del st.session_state.delete_truck_id
                st.experimental_rerun()

# Add/Edit truck view
def add_truck():
    st.markdown('<div class="admin-section"><h3>Adicionar/Editar Caminhão</h3></div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Check if we're editing
    editing = False
    truck_data = {}
    
    if hasattr(st.session_state, 'edit_truck_id'):
        truck_id = st.session_state.edit_truck_id
        if truck_id in df['truck_id'].values:
            editing = True
            truck_data = df[df['truck_id'] == truck_id].iloc[0].to_dict()
    
    # Form for adding/editing truck
    with st.form("truck_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            brand = st.text_input("Marca", value=truck_data.get('brand', ''))
            model = st.text_input("Modelo", value=truck_data.get('model', ''))
            year = st.number_input("Ano", min_value=1950, max_value=datetime.now().year + 1, value=int(truck_data.get('year', datetime.now().year)))
            mileage = st.number_input("Quilometragem (km)", min_value=0, value=int(truck_data.get('mileage', 0)))
            truck_type = st.selectbox("Tipo", options=['Cavalo Mecânico', 'Truck', 'Toco', 'Bitruck', 'VUC', 'Outro'], index=0 if 'truck_type' not in truck_data else ['Cavalo Mecânico', 'Truck', 'Toco', 'Bitruck', 'VUC', 'Outro'].index(truck_data['truck_type']))
        
        with col2:
            transmission = st.selectbox("Transmissão", options=['Manual', 'Automática', 'Automatizada'], index=0 if 'transmission' not in truck_data else ['Manual', 'Automática', 'Automatizada'].index(truck_data['transmission']))
            engine = st.text_input("Motor", value=truck_data.get('engine', ''))
            condition = st.selectbox("Condição", options=['Novo', 'Seminovo', 'Usado'], index=0 if 'condition' not in truck_data else ['Novo', 'Seminovo', 'Usado'].index(truck_data['condition']))
            status = st.selectbox("Status", options=['Disponível', 'Vendido', 'Em Manutenção', 'Reservado'], index=0 if 'status' not in truck_data else ['Disponível', 'Vendido', 'Em Manutenção', 'Reservado'].index(truck_data['status']))
            price = st.number_input("Preço (R$)", min_value=0.0, value=float(truck_data.get('price', 0.0)))
        
        features = st.text_area("Características/Detalhes", value=truck_data.get('features', ''))
        
        sales_person = st.selectbox("Vendedor", options=['Rapha', 'Vendedor 2', 'Vendedor 3'], index=0 if 'sales_person' not in truck_data else ['Rapha', 'Vendedor 2', 'Vendedor 3'].index(truck_data['sales_person']))
        
        upload_image = st.file_uploader("Foto do Caminhão", type=["jpg", "jpeg", "png"])
        
        if editing:
            submit_text = "Atualizar Caminhão"
        else:
            submit_text = "Adicionar Caminhão"
            
        submitted = st.form_submit_button(submit_text)
        
        if submitted:
            # Generate truck ID if new truck
            if not editing:
                truck_id = str(uuid.uuid4())
                upload_date = datetime.now().strftime("%Y-%m-%d")
                sale_date = None
            else:
                truck_id = truck_data['truck_id']
                upload_date = truck_data['upload_date']
                sale_date = truck_data['sale_date']
            
            # Handle image
            photo_path = truck_data.get('photo_path', None)
            if upload_image is not None:
                photo_path = save_image(upload_image, truck_id)
            
            # Create new row
            new_data = {
                'truck_id': truck_id,
                'brand': brand,
                'model': model,
                'year': year,
                'mileage': mileage,
                'truck_type': truck_type,
                'transmission': transmission,
                'engine': engine,
                'features': features,
                'condition': condition,
                'status': status,
                'price': price,
                'upload_date': upload_date,
                'sale_date': sale_date,
                'sales_person': sales_person,
                'photo_path': photo_path
            }
            
            if editing:
                # Update existing truck
                df.loc[df['truck_id'] == truck_id] = pd.Series(new_data)
                message = "Caminhão atualizado com sucesso!"
            else:
                # Add new truck
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                message = "Caminhão adicionado com sucesso!"
            
            # Save updated dataframe
            save_data(df)
            
            st.success(message)
            
            # Reset editing state if we were editing
            if editing:
                del st.session_state.edit_truck_id
                st.session_state.current_view = "inventory"
                st.experimental_rerun()

# Analytics view
def analytics_view():
    st.markdown('<div class="admin-section"><h3>Análises e Relatórios</h3></div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.info("Não há dados suficientes para análise. Adicione caminhões ao inventário primeiro.")
        return
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Caminhões", len(df))
    
    with col2:
        available_count = len(df[df['status'] == 'Disponível'])
        st.metric("Caminhões Disponíveis", available_count)
    
    with col3:
        sold_count = len(df[df['status'] == 'Vendido'])
        st.metric("Caminhões Vendidos", sold_count)
    
    with col4:
        if 'price' in df.columns and 'status' in df.columns:
            sold_df = df[df['status'] == 'Vendido']
            if not sold_df.empty:
                total_sales = sold_df['price'].sum()
                st.metric("Valor Total de Vendas", f"R$ {total_sales:,.2f}".replace(',', '.'))
            else:
                st.metric("Valor Total de Vendas", "R$ 0,00")
    
    st.markdown("---")
    
    # More detailed analytics
    if len(df) > 1:
        # Truck brands distribution
        st.subheader("Distribuição por Marca")
        brand_counts = df['brand'].value_counts().reset_index()
        brand_counts.columns = ['Marca', 'Quantidade']
        fig = px.bar(brand_counts, x='Marca', y='Quantidade', color='Marca')
        st.plotly_chart(fig, use_container_width=True)
        
        # Status distribution
        st.subheader("Distribuição por Status")
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Quantidade']
        fig = px.pie(status_counts, names='Status', values='Quantidade')
        st.plotly_chart(fig, use_container_width=True)
        
        # Sales by month (if there are sold trucks)
        sold_df = df[df['status'] == 'Vendido'].copy()
        if not sold_df.empty and 'sale_date' in sold_df.columns:
            st.subheader("Vendas por Mês")
            
            # Convert sale_date to datetime
            sold_df['sale_date'] = pd.to_datetime(sold_df['sale_date'])
            sold_df['month'] = sold_df['sale_date'].dt.strftime('%Y-%m')
            
            monthly_sales = sold_df.groupby('month')['price'].sum().reset_index()
            monthly_sales.columns = ['Mês', 'Valor Total']
            
            fig = px.line(monthly_sales, x='Mês', y='Valor Total', markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # Sales by vendor
            st.subheader("Vendas por Vendedor")
            vendor_sales = sold_df.groupby('sales_person').agg({
                'truck_id': 'count',
                'price': 'sum'
            }).reset_index()
            
            vendor_sales.columns = ['Vendedor', 'Quantidade Vendida', 'Valor Total']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(vendor_sales, x='Vendedor', y='Quantidade Vendida', color='Vendedor')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(vendor_sales, x='Vendedor', y='Valor Total', color='Vendedor')
                st.plotly_chart(fig, use_container_width=True)

# Settings view
def settings_view():
    st.markdown('<div class="admin-section"><h3>Configurações</h3></div>', unsafe_allow_html=True)
    
    st.subheader("Exportar Dados")
    
    # Load data
    df = load_data()
    
    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Baixar Inventário (CSV)",
            data=csv,
            file_name="consulting_truck_inventory.csv",
            mime="text/csv"
        )
    
    st.subheader("Importar Dados")
    
    uploaded_file = st.file_uploader("Carregar arquivo CSV", type=["csv"])
    
    if uploaded_file is not None:
        try:
            imported_df = pd.read_csv(uploaded_file)
            required_columns = ['truck_id', 'brand', 'model', 'year', 'status']
            
            if all(col in imported_df.columns for col in required_columns):
                if st.button("Confirmar Importação"):
                    # Backup current data
                    if os.path.exists(CSV_PATH):
                        backup_path = f"{CSV_PATH}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        os.rename(CSV_PATH, backup_path)
                    
                    # Save imported data
                    imported_df.to_csv(CSV_PATH, index=False)
                    st.success("Dados importados com sucesso!")
                    st.experimental_rerun()
            else:
                st.error("O arquivo não contém todas as colunas necessárias.")
        except Exception as e:
            st.error(f"Erro ao importar arquivo: {str(e)}")

# Main app
def main():
    load_css()
    
    # Check if authenticated
    if not st.session_state.authenticated:
        login_form()
    else:
        admin_view()

if __name__ == "__main__":
    main()
