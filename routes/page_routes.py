# routes/page_routes.py
from flask import Blueprint, render_template, redirect, url_for, session

page_bp = Blueprint('pages', __name__)

@page_bp.route('/')
def index():
    """Home page"""
    return render_template('dashboard.html')

@page_bp.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@page_bp.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@page_bp.route('/register')
def register_page():
    """Register page"""
    return render_template('register.html')

@page_bp.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    return redirect(url_for('pages.index'))