APX WINDOWS — REGRESSO AUTOMÁTICO

Na primeira sessão, aceita uma vez o pedido de administrador para instalar
APX-LinuxDefault-v1. Depois, a tarefa de sistema seleciona Linux ao arrancar
o Windows e ao iniciar sessão, sem pedir autorização novamente.

Usa Reiniciar normalmente para regressar ao APX. Não há atalhos de teclado
APX e WIN+E mantém a função normal do Windows. A tarefa não reinicia sozinha.

Se cancelares a instalação, será proposta na próxima sessão. Até estar
instalada e validada, o regresso automático não está garantido.
Erros: C:\ProgramData\APX\ReturnToHub\ReturnToHub.log
Remover tarefa (PowerShell como administrador):
& "$env:ProgramData\APX\ReturnToHub\APX-ReturnToHub.ps1" -Remove
