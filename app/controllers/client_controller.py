from flask import Blueprint, render_template

client_bp = Blueprint("client", __name__)


# ==================== VISTAS CLIENTE ====================

@client_bp.get("/")
def client_dashboard_view():
    """Vista del dashboard del cliente (padre/tutor)."""
    return render_template("client/dashboard.html")


@client_bp.get("/profile")
def client_profile_view():
    """Vista del perfil del cliente y sus hijos vinculados."""
    return render_template("client/profile.html")


@client_bp.get("/reports")
def client_reports_view():
    """Vista de reportes con filtros y gráficos."""
    return render_template("client/reports.html")


@client_bp.get("/settings")
def client_settings_view():
    """Vista de configuración y privacidad del cliente."""
    return render_template("client/settings.html")


@client_bp.get("/policy")
def client_policy_view():
    """Vista de política universitaria."""
    return render_template("client/policy.html")