#!/usr/bin/env python3
"""
Script para criar usuário admin de teste no ECOA
Execute: python -m scripts.create_admin
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import User, PlanType
from app.services.auth import get_password_hash


def create_admin_user():
    """Cria usuário admin de teste"""

    # Credenciais do admin
    ADMIN_EMAIL = "admin@ecoa.com.br"
    ADMIN_PASSWORD = "Admin@123456"

    print("=" * 50)
    print("ECOA - Criação de Usuário Admin")
    print("=" * 50)

    # Inicializar banco de dados (criar tabelas se não existirem)
    print("\n1. Inicializando banco de dados...")
    try:
        init_db()
        print("   ✓ Tabelas criadas/verificadas com sucesso!")
    except Exception as e:
        print(f"   ✗ Erro ao inicializar banco: {e}")
        return False

    # Criar sessão
    db = SessionLocal()

    try:
        # Verificar se admin já existe
        print("\n2. Verificando se admin já existe...")
        existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()

        if existing:
            print(f"   ! Usuário {ADMIN_EMAIL} já existe!")
            print(f"   ID: {existing.id}")
            print(f"   Plano: {existing.plan_type.value}")
            return True

        # Criar novo admin
        print("\n3. Criando usuário admin...")
        hashed_password = get_password_hash(ADMIN_PASSWORD)

        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=hashed_password,
            full_name="Administrador",
            political_name="Admin ECOA",
            party="ADMIN",
            state="SP",
            plan_type=PlanType.PRO,
            is_active=True,
            is_verified=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("   ✓ Usuário admin criado com sucesso!")
        print("\n" + "=" * 50)
        print("CREDENCIAIS DO ADMIN:")
        print("=" * 50)
        print(f"Email:    {ADMIN_EMAIL}")
        print(f"Senha:    {ADMIN_PASSWORD}")
        print(f"ID:       {admin.id}")
        print(f"Plano:    {admin.plan_type.value}")
        print("=" * 50)

        return True

    except Exception as e:
        db.rollback()
        print(f"   ✗ Erro ao criar admin: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = create_admin_user()
    sys.exit(0 if success else 1)
