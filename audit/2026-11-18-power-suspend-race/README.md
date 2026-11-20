## Encerramento e suspensão pela tampa — 2026-11-18

O proprietário reportou ecrã preto ao voltar a ligar e autorizou a correção.
Os registos de 18/11 mostram poweroff às 19:21:55 seguido de Lid closed e
suspensão às 19:21:57–58; status.json guardou recusa de PowerOff por suspensão
já em curso. Outra tentativa falhou na recuperação de tty1 após suspensão.
O runner instalado adquire systemd-inhibit sleep:handle-lid-switch antes de
fechar a sessão e mantém a proteção durante a transição. Suspensão explícita
conserva a sessão. Em erro após iniciar o encerramento, liberta o lock e pede
arranque do supervisor do Hub, preservando o estado failed e o erro original.
Não se relaxaram verificações de identidade, recuperação ou máquinas restantes.

19 testes passaram (10 físicos/fluxo, 9 contrato); aquisição real do inibidor
verificada sem ação de energia. Fonte e runner instalado idênticos; backup em
`/var/lib/apx/backups/20261118-power-suspend-race/`. Não foi executado poweroff,
reboot nem suspensão para preservar a sessão. A confirmação física num ciclo
completo permanece pendente; não se afirma resolução de todos os ecrãs pretos.
Sem commit/push.

