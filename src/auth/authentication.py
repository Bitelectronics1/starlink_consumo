#!/usr/bin/env python3
"""
Sistema de autenticação para Starlink Data Analyzer
"""

import streamlit as st
import hashlib
import os
from datetime import datetime, timedelta

def hash_password(password: str) -> str:
    """Gera hash SHA-256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password() -> bool:
    """Verifica se a senha está correta"""
    
    # Verifica se já está autenticado
    if st.session_state.get("authenticated", False):
        return True
    
    # Verifica se a sessão ainda é válida (24 horas)
    if "auth_time" in st.session_state:
        auth_time = st.session_state["auth_time"]
        if datetime.now() - auth_time < timedelta(hours=24):
            return True
        else:
            # Sessão expirada
            st.session_state["authenticated"] = False
            st.session_state.pop("auth_time", None)
    
    # Obtém a senha do ambiente
    correct_password = os.environ.get("STARLINK_PASSWORD", "")
    
    if not correct_password:
        st.error("❌ Senha não configurada no servidor!")
        return False
    
    # Interface de login
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 Starlink Data Analyzer</h1>
        <p style="color: #666; font-size: 1.1rem;">Acesso restrito à equipe interna</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulário de login
    with st.form("login_form"):
        st.markdown("### 🔑 Autenticação")
        
        password = st.text_input(
            "Senha de acesso:",
            type="password",
            placeholder="Digite a senha...",
            help="Entre em contato com a equipe para obter a senha de acesso"
        )
        
        submitted = st.form_submit_button("🚀 Entrar", use_container_width=True)
        
        if submitted:
            if password:
                # Verifica a senha
                if hash_password(password) == hash_password(correct_password):
                    st.session_state["authenticated"] = True
                    st.session_state["auth_time"] = datetime.now()
                    st.success("✅ Acesso autorizado!")
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
                    st.session_state["authenticated"] = False
            else:
                st.error("❌ Digite a senha!")
    
    # Informações de contato
    st.markdown("""
    ---
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>🔒 Acesso restrito à equipe Bit Electronics</p>
        <p>Para obter acesso, entre em contato com a administração</p>
    </div>
    """, unsafe_allow_html=True)
    
    return False

def logout():
    """Faz logout do usuário"""
    st.session_state["authenticated"] = False
    st.session_state.pop("auth_time", None)
    st.rerun()

def show_logout_button():
    """Mostra botão de logout na sidebar"""
    if st.session_state.get("authenticated", False):
        with st.sidebar:
            st.markdown("---")
            if st.button("🚪 Sair", use_container_width=True):
                logout()
            
            # Mostra tempo restante da sessão
            if "auth_time" in st.session_state:
                auth_time = st.session_state["auth_time"]
                remaining_time = timedelta(hours=24) - (datetime.now() - auth_time)
                if remaining_time.total_seconds() > 0:
                    hours = int(remaining_time.total_seconds() // 3600)
                    minutes = int((remaining_time.total_seconds() % 3600) // 60)
                    st.caption(f"⏰ Sessão expira em: {hours}h {minutes}m")
                else:
                    st.caption("⏰ Sessão expirada")
                    logout()

def require_auth(func):
    """Decorator para exigir autenticação"""
    def wrapper(*args, **kwargs):
        if check_password():
            return func(*args, **kwargs)
        else:
            return None
    return wrapper
