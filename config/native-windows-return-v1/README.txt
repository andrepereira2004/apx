APX RETURN TO HUB

SUPER+E seleciona o Linux Boot Manager na UEFI, reinicia o Windows e regressa
ao APX. O Windows pede autorizacao de administrador para esta alteracao de
arranque. Se a selecao falhar ou for recusada, o Windows nao reinicia.
O helper interceta a combinacao
antes do Explorer apenas enquanto está ativo; fora dele, WIN+E mantém o
comportamento normal do Windows.

O helper arranca oculto em segundo plano a cada início de sessão e volta a
tentar automaticamente se o hook de teclado ainda não estiver disponível.
O diagnóstico fica em %LOCALAPPDATA%\APX\ReturnToHub.log. Não é colocado
qualquer ícone APX no Ambiente de Trabalho.

Ao iniciar sessão, o helper não pede autorização de administrador. A autorização
é pedida apenas quando usa SUPER+E para regressar ao APX.
O atalho acompanha as teclas Win diretamente e recupera o hook a cada 20 s.
