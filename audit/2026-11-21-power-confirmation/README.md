## Confirmação de desligar/reiniciar — 2026-11-21

Removida a confirmação automática de poweroff/reboot no shell. A preparação
abre o cartão Cancelar/Desligar ou Cancelar/Reiniciar e só a confirmação
explícita inicia a transição. Suspensão automática por inatividade preservada.
Instaladas apenas as alterações revistas em seis homes/seed, preservando as
outras diferenças; pins sincronizados. 19 testes de energia e oito seed passaram;
teste JS executou os callbacks reais de preparação e confirmação para ambas as
ações. Na sessão Finanças, prepareShutdown permaneceu preparado à espera e
cancelShutdown fechou o pedido; nenhum desligar/reiniciar foi executado.
Backup: /var/lib/apx/backups/20261121T161209Z-power-confirmation.
Native continua enabled, sem erros. Sem commit/push.

