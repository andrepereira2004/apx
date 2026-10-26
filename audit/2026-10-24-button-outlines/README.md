# Contornos dos botões QuickShell — 24/10/2026

Contorno comum ButtonOutline.qml, baseado nos workspaces: 1 px, margem interior de
1 px, cantos derivados do botão, branco #d9dcea quando selecionado/focado e cinzento
#69728a no hover. Estado selecionado tem prioridade sobre hover.

Aplicado a BarButton (incluindo workspaces, Environment e ações da barra), MediaIsland,
MenuHover e RadioIconButton. ControlTile e escolhas dos menus usam o contorno comum;
os contornos antigos são suspensos durante o realce para evitar duas linhas sobrepostas.
Botões de ação deixaram de ter hover de2px; a borda selecionada já não depende da cor
de ícones. Campos de texto, molduras de painéis e indicadores de erro não são botões.

Fonte, seed e cinco ambientes sincronizados; hashes runtime/recovery atualizados.
7 testes de seed e8 de notificações passaram. Última verificação: zero alterações
pendentes. Captura visual confirma menus e cantos arredondados; aceitação do utilizador
pendente. Na primeira recarga houve incompatibilidade transitória entre ficheiros
antigos/novos; recarga final concluída e shell pronta. Sem mudança de compositor.

Backups consecutivos desta alteração:20261024T074004Z-controls-followup,
20261024T074234Z-controls-followup e20261024T074430Z-controls-followup em
/var/lib/apx/backups. O primeiro permite recuperar o estado anterior completo.
CPU em cpu-after.json foi medida durante abertura/uso de controlos; não comparar
com os2–3% anteriores de menus fechados. Sem medição de FPS nesta alteração.
