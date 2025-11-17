import os
from flask import Blueprint

# Sirve los assets del template KaiAdmin desde la carpeta añadida por el usuario
# Ruta esperada: <repo_root>/kaiadmin-lite-1.2.0/assets
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_kaiadmin_assets_path = os.path.join(_repo_root, 'kaiadmin-lite-1.2.0', 'assets')
_axis_assets_path = os.path.join(_repo_root, 'Axis', 'Axis', 'assets')

# Blueprint de estáticos adicionales en /kaiadmin/*
kaiadmin_bp = Blueprint(
    'kaiadmin_assets', __name__,
    static_folder=_kaiadmin_assets_path,
    static_url_path='/kaiadmin'
)

# Blueprint de estáticos para el template Axis en /axis/*
axis_bp = Blueprint(
    'axis_assets', __name__,
    static_folder=_axis_assets_path,
    static_url_path='/axis'
)

# Ruta de diagnóstico para verificar que la carpeta existe
@kaiadmin_bp.route('/_debug_exists')
def _debug_exists():
    exists = os.path.isdir(_kaiadmin_assets_path)
    return {'path': _kaiadmin_assets_path, 'exists': exists}

@axis_bp.route('/_debug_exists')
def _debug_exists_axis():
    exists = os.path.isdir(_axis_assets_path)
    return {'path': _axis_assets_path, 'exists': exists}