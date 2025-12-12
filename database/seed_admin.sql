-- =====================================================
-- SCRIPT PARA CRIAR USUÁRIO ADMIN NO ECOA
-- Execute este script no SQL Editor do Supabase
-- =====================================================

-- Credenciais do Admin:
-- Email: admin@ecoa.com.br
-- Senha: Admin@123456

-- Criar usuário no auth.users (isso só funciona se você tiver permissões de service_role)
-- Se não funcionar, crie manualmente via Dashboard > Authentication > Add User

-- Inserir perfil admin (assumindo que o usuário já foi criado no Auth)
DO $$
DECLARE
    admin_user_id UUID;
BEGIN
    -- Buscar o ID do usuário admin
    SELECT id INTO admin_user_id
    FROM auth.users
    WHERE email = 'admin@ecoa.com.br'
    LIMIT 1;

    -- Se encontrou o usuário, criar/atualizar o perfil
    IF admin_user_id IS NOT NULL THEN
        INSERT INTO ecoa_profiles (
            id,
            full_name,
            political_name,
            party,
            state,
            plan_type
        ) VALUES (
            admin_user_id,
            'Administrador',
            'Admin ECOA',
            'ADMIN',
            'SP',
            'pro'
        )
        ON CONFLICT (id) DO UPDATE SET
            plan_type = 'pro',
            full_name = 'Administrador',
            political_name = 'Admin ECOA';

        RAISE NOTICE 'Perfil admin criado/atualizado com sucesso! ID: %', admin_user_id;
    ELSE
        RAISE NOTICE 'Usuário admin@ecoa.com.br não encontrado. Crie primeiro via Dashboard > Authentication > Add User';
    END IF;
END $$;

-- Verificar resultado
SELECT
    p.id,
    p.full_name,
    p.political_name,
    p.plan_type,
    u.email
FROM ecoa_profiles p
JOIN auth.users u ON u.id = p.id
WHERE u.email = 'admin@ecoa.com.br';
