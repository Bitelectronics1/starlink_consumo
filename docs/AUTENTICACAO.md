# 🔐 Sistema de Autenticação - Starlink Data Analyzer

Sistema de autenticação por senha para proteger o acesso ao sistema.

## 🛡️ Como Funciona

### Autenticação por Senha
- **Senha única** para toda a equipe
- **Sessão de 24 horas** - não precisa digitar a senha toda vez
- **Hash SHA-256** - senha não fica exposta no código
- **Logout automático** após expiração

### Interface de Login
- Tela de login elegante
- Campo de senha protegido
- Mensagens de erro claras
- Botão de logout na sidebar

## ⚙️ Configuração

### 1. Variável de Ambiente
```bash
# No arquivo .env ou variáveis do Portainer
STARLINK_PASSWORD=senha_da_equipe_interna
```

### 2. Exemplo de Senha Forte
```bash
# Recomendado: senha com 12+ caracteres
STARLINK_PASSWORD=BitEletronics2024!
```

### 3. Configuração no Portainer
1. Acesse a stack `starlink-analyzer`
2. Clique em "Editor"
3. Adicione a variável:
   ```yaml
   environment:
     - INFLUXDB_TOKEN=${INFLUXDB_TOKEN}
     - STARLINK_PASSWORD=${STARLINK_PASSWORD}
   ```
4. Configure a variável no Portainer:
   - Nome: `STARLINK_PASSWORD`
   - Valor: `sua_senha_secreta`

## 🔒 Segurança

### Recursos de Segurança
- **Hash SHA-256** - senha não fica em texto plano
- **Sessão temporária** - expira em 24 horas
- **Logout automático** - após expiração
- **Verificação contínua** - a cada acesso

### Boas Práticas
1. **Senha forte**: Use 12+ caracteres com números e símbolos
2. **Não compartilhe**: Mantenha a senha apenas com a equipe
3. **Altere regularmente**: Mude a senha periodicamente
4. **Monitore acessos**: Verifique logs de acesso

## 🚀 Como Usar

### Para Usuários
1. Acesse a aplicação
2. Digite a senha da equipe
3. Clique em "Entrar"
4. Use o sistema normalmente
5. Para sair, clique em "Sair" na sidebar

### Para Administradores
1. Configure a senha no Portainer
2. Informe a senha para a equipe
3. Monitore acessos nos logs
4. Altere a senha quando necessário

## 🔧 Solução de Problemas

### Erro: "Senha não configurada"
- Verifique se `STARLINK_PASSWORD` está definida
- Confirme se a variável está no Portainer
- Reinicie os containers após configurar

### Erro: "Senha incorreta"
- Verifique se a senha está correta
- Confirme se não há espaços extras
- Teste com uma senha simples primeiro

### Sessão expirada
- Faça login novamente
- A sessão expira em 24 horas
- Isso é normal por segurança

## 📱 Interface

### Tela de Login
```
🔐 Starlink Data Analyzer
Acesso restrito à equipe interna

🔑 Autenticação
Senha de acesso: [campo protegido]
[🚀 Entrar]

🔒 Acesso restrito à equipe Bit Electronics
Para obter acesso, entre em contato com a administração
```

### Após Login
- Botão "🚪 Sair" na sidebar
- Contador de tempo restante da sessão
- Acesso completo ao sistema

## 🔄 Atualizações

### Alterar Senha
1. No Portainer, altere a variável `STARLINK_PASSWORD`
2. Reinicie os containers
3. Informe a nova senha para a equipe

### Desabilitar Autenticação
1. Remova a variável `STARLINK_PASSWORD`
2. Reinicie os containers
3. O sistema ficará sem autenticação

## 📊 Monitoramento

### Logs de Acesso
- Verifique logs no Portainer
- Monitore tentativas de login
- Identifique acessos suspeitos

### Métricas
- Número de logins por dia
- Tempo de sessão médio
- Tentativas de senha incorreta

---

**🔐 Sistema de Autenticação** - Proteção de acesso para equipe interna
