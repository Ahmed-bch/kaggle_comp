# app.py - Version corrigée pour streamlit-authenticator v0.3+
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Configuration de la page
st.set_page_config(
    page_title="App Sécurisée",
    page_icon="🔐",
    layout="wide"
)

# Chargement de la configuration
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# NOUVELLE SYNTAXE pour v0.3+ - Simplifiée !
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
    # PLUS de paramètre 'preauthorized' ici !
)

# Interface de connexion
name, authentication_status, username = authenticator.login()

# Gestion des états d'authentification
if authentication_status == False:
    st.error('❌ Nom d\'utilisateur ou mot de passe incorrect')
elif authentication_status == None:
    st.warning('⚠️ Veuillez entrer votre nom d\'utilisateur et mot de passe')
elif authentication_status:
    # Interface pour utilisateur connecté
    st.title(f'🎉 Bienvenue {name}!')
    
    # Sidebar avec logout
    with st.sidebar:
        st.write(f'👤 Connecté en tant que **{name}**')
        st.write(f'📧 Email: {config["credentials"]["usernames"][username]["email"]}')
        st.divider()
        authenticator.logout('🚪 Se déconnecter', 'sidebar')
    
    # Contenu principal
    st.header('📊 Tableau de bord')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Utilisateurs actifs", "1,234", delta="12")
    with col2:
        st.metric("📈 Projets", "42", delta="3")
    with col3:
        st.metric("⏱️ Temps total", "156h", delta="8h")
    
    # Zone protégée
    st.header('🔒 Contenu protégé')
    st.success('✅ Ce contenu n\'est visible que pour les utilisateurs connectés!')
    
    # Exemple de fonctionnalités
    tab1, tab2, tab3 = st.tabs(["📈 Données", "⚙️ Paramètres", "👤 Profil"])
    
    with tab1:
        st.subheader('Graphique des ventes')
        import pandas as pd
        import numpy as np
        
        # Données d'exemple
        data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
            'Ventes': np.random.randint(50, 200, 30),
            'Visiteurs': np.random.randint(500, 2000, 30)
        })
        
        st.line_chart(data.set_index('Date'))
        st.dataframe(data.tail(), use_container_width=True)
        
    with tab2:
        st.subheader('⚙️ Paramètres utilisateur')
        if username == 'admin':
            st.info('🔧 **Mode Administrateur activé**')
            st.selectbox('Thème système', ['Clair', 'Sombre', 'Auto'])
            st.slider('Limite utilisateurs', 1, 100, 50)
        else:
            st.selectbox('Thème', ['Clair', 'Sombre'])
            st.slider('Notifications', 0, 10, 5)
            
    with tab3:
        st.subheader(f'👤 Profil de {name}')
        
        user_info = config["credentials"]["usernames"][username]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f'**Nom complet:** {user_info["name"]}')
            st.info(f'**Nom d\'utilisateur:** {username}')
        with col2:
            st.info(f'**Email:** {user_info["email"]}')
            st.info(f'**Statut:** {"Admin" if username == "admin" else "Utilisateur"}')
        
        # Bouton pour modifier le profil (fonctionnalité avancée)
        if st.button('✏️ Modifier les détails'):
            # Utilisation de la nouvelle méthode pour modifier les détails
            if authenticator.update_user_details(username, 'main'):
                st.success('✅ Profil mis à jour avec succès!')
                st.experimental_rerun()

    # Section pour l'enregistrement de nouveaux utilisateurs (si admin)
    if username == 'admin':
        st.header('👥 Gestion des utilisateurs')
        
        with st.expander('➕ Enregistrer un nouvel utilisateur'):
            # Nouvelle syntaxe pour l'enregistrement
            try:
                email, username_new, name_new = authenticator.register_user(
                    location='main',
                    pre_authorized=None  # Pas de restriction
                )
                if email:
                    st.success(f'✅ Utilisateur {username_new} enregistré avec succès!')
                    st.info('💾 N\'oubliez pas de sauvegarder le fichier config.yaml mis à jour!')
                    
                    # Afficher le config mis à jour
                    st.code(yaml.dump(config, default_flow_style=False))
                    
            except Exception as e:
                st.error(f'❌ Erreur lors de l\'enregistrement: {e}')
                
    # Section pour réinitialiser le mot de passe
    st.header('🔑 Gestion du mot de passe')
    
    with st.expander('🔄 Réinitialiser mon mot de passe'):
        if authenticator.reset_password(username, 'main'):
            st.success('✅ Mot de passe modifié avec succès!')
            st.info('💾 N\'oubliez pas de sauvegarder le fichier config.yaml mis à jour!')

# Sauvegarder les modifications dans le config
try:
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
except Exception as e:
    if 'authentication_status' in locals() and authentication_status:
        st.error(f'❌ Impossible de sauvegarder les modifications: {e}')
