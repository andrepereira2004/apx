# Aplicações atuais em novos Environments — 2026-11-21

Instalado no piloto: o runtime consulta a versão estável de cada pacote externo
antes da instalação. Pacotes Arch já usavam -Syu no root do Environment.
O novo módulo não instala aplicações no Host: prepara apenas artefactos verificados.
A falta de rede, checksum, assinatura ou identidade impede a instalação e não
aceita silenciosamente o cache antigo. NVIDIA continua ligada à versão do módulo
Host e Salvador de Mundos à versão interna APX, não a um fornecedor externo.

Brave: artefacto antigo 1:1.93.136-1 substituído no catálogo por 1:1.100.58-1.
Zip oficial SHA-256 verificado; executável real respondeu
«Brave Browser 158.1.100.58 unknown» num diretório descartável dentro de Finanças,
sem abrir navegador nem tocar no perfil. Launcher, ícones e .desktop conservados.

ChatGPT: índice e pacote oficial assinados verificados com a chave pública já
revista, fingerprint 3BFA0E4AE8B8CC16A2D9BA684A3B4A566C4660E4. Catálogo atualizado
para 26.1117.41037-1. Chave pública exportada para
/usr/share/apx/chatgpt-release-keyring.gpg; cópia pública neste audit.
LocalSend 1.18.2 continua atual; futuras versões usam arquivo oficial verificado.
GridCraft 0.19.1, WordCraft 0.18.1 e DeckCraft 0.18.1 preparados dos pacotes oficiais.
Normalizada apenas a identidade do pacote para conservar a integração APX;
DeckCraft conserva wrapper de escala e pin de versão atualizado. Patches binários
antigos não foram reaplicados a versões diferentes. Abrir documentos/jogos e
aceitação visual destas novas versões ainda não foram exercitados fisicamente.
Nenhuma aplicação existente foi atualizada ou reiniciada nesta tarefa.

VS Code consulta metadados estáveis Microsoft e verifica o SHA-256. BedrockOnLinux
consulta a release estável GitHub e verifica o SHA-256 do AppImage. Minecraft usa
URL atual do fornecedor, em vez do checksum de agosto numa URL mutável. Hytale
já usa URL latest. Aplicações Flatpak resolvem o remoto estável.

Validação: sete testes novos (metadados estáveis, digest/URL, preservação Brave,
traversal, falha de rede sem fallback, cache atual e identidade ArtCraft), doze
testes features, cinco defaults e oito seed passaram. bash -n do script de apps
passou. Todas as seis resoluções reais de fornecedores repetidas no módulo
instalado: resolved-versions.json. As instalações completas de novos Environments
não foram executadas; não afirmar validação gráfica integral por aplicação.

Backup Host: /var/lib/apx/backups/20261121T162351Z-fresh-app-installs.
Manifests anteriores e pacotes antigos conservados em /var/lib/apx/package-artifacts;
manifestos *.before-*.json permitem repor o catálogo sem reinstalar pacotes Host.
Runtime fonte/instalado preservam os seus próprios pins de seed; recuperação
sincronizada. Native enabled=true e sem erros. Sem commit/push.
