#!/usr/bin/env python3
"""
Script para corregir valores de Enum en la base de datos.
Cambiar 'ausente' a 'falta' en la tabla attendance.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models import Attendance
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        print("Conectando a la base de datos...")
        
        # Contar registros con 'ausente'
        ausente_count = db.session.query(Attendance).filter(
            Attendance.status == 'ausente'
        ).count()
        
        print(f"✓ Encontrados {ausente_count} registros con status='ausente'")
        
        if ausente_count > 0:
            print("Actualizando registros con 'ausente'...")
            db.session.query(Attendance).filter(
                Attendance.status == 'ausente'
            ).update({Attendance.status: 'falta'})
            db.session.commit()
            print("✓ Registros actualizados a status='falta'")
        
        # Corregir 'salida_temprana' a 'salida_repentina'
        salida_temprana_count = db.session.query(Attendance).filter(
            Attendance.status == 'salida_temprana'
        ).count()
        
        if salida_temprana_count > 0:
            print(f"Encontrados {salida_temprana_count} registros con status='salida_temprana'")
            print("Actualizando registros con 'salida_temprana'...")
            db.session.query(Attendance).filter(
                Attendance.status == 'salida_temprana'
            ).update({Attendance.status: 'salida_repentina'})
            db.session.commit()
            print("✓ Registros actualizados a status='salida_repentina'")
        
        # Verificar valores válidos
        print("\nVerificando valores en tabla attendance...")
        statuses = db.session.query(Attendance.status.distinct()).all()
        print(f"Valores únicos de status: {[s[0] for s in statuses]}")
        
        print("\n✅ Base de datos corregida correctamente")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.session.rollback()
        sys.exit(1)
