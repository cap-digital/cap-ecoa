-- Script para criar usuário admin no ECOA
-- Execute este script no SQL Editor do Supabase APÓS criar o usuário via Authentication

-- 1. Primeiro, encontre o ID do usuário criado no Auth
-- Você pode ver isso em Authentication > Users no dashboard

-- 2. Substitua 'SEU_USER_ID_AQUI' pelo ID real do usuário
-- e execute o comando abaixo:

/*
INSERT INTO ecoa_profiles (
    id,
    full_name,
    political_name,
    party,
    state,
    plan_type
) VALUES (
    'SEU_USER_ID_AQUI',  -- Substitua pelo UUID do usuário
    'Administrador',
    'Admin ECOA',
    'ADMIN',
    'SP',
    'pro'  -- Plano PRO com acesso ilimitado
) ON CONFLICT (id) DO UPDATE SET
    plan_type = 'pro',
    full_name = 'Administrador';
*/

-- OU use este comando que cria automaticamente para o último usuário criado:
INSERT INTO ecoa_profiles (
    id,
    full_name,
    political_name,
    party,
    state,
    plan_type
)
SELECT
    id,
    COALESCE(raw_user_meta_data->>'full_name', 'Administrador'),
    'Admin ECOA',
    'ADMIN',
    'SP',
    'pro'
FROM auth.users
WHERE email = 'admin@ecoa.com.br'
ON CONFLICT (id) DO UPDATE SET
    plan_type = 'pro',
    full_name = 'Administrador',
    political_name = 'Admin ECOA';

-- Verificar se foi criado corretamente
SELECT * FROM ecoa_profiles WHERE full_name = 'Administrador';
