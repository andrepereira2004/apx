# Logitech G305 — investigação e mitigação persistente

Os registos mostram falhas USB de descritor/protocolo no hub Genesys05e3:0610,
primeiro na porta1-2.3 e depois na1-2.2. O recetor046d:c53f também foi utilizado
diretamente em3-2; o utilizador confirmou que o retirou porque deixou de responder.
Isso não permite tratar a desconexão manual como uma falha espontânea, nem atribuir
a causa exclusivamente ao hub. Os resets observados não coincidiram com ações do
serviço APX de recuperação; não foram registadas tentativas de recuperação nesses
momentos. A suspensão automática do recetor já estava desativada quando observado.

Aplicado:
- Regra persistente85-apx-logitech-stability.rules, apenas para recetor046d:c53f e
  hub05e3:0610: power/control=on em add/bind. Não desativa suspensão de outros USB
  nem suspensão global do portátil. Atributo do hub mudou de auto para on.
- Serviço existente conserva a recuperação limitada a uma tentativa por identidade
  do recetor. Acrescentado diagnóstico só quando muda o estado (porta, presença do
  dispositivo de entrada G305 e energia), sem recolher movimentos/teclas.
- Retirar o USB durante a consulta deixa de marcar a execução como falhada.
  Nenhum daemon adicional e nenhum reset do controlador inteiro.

Validação: regra udev válida; serviço success/0;4 testes passaram, incluindo não
reiniciar um rato saudável, não repetir resets, não reescrever estado inalterado e
aceitar desconexão durante consulta. A última observação não encontrou o recetor;
falta validar estabilidade com ele ligado. Foram observadas novas falhas em1-2.2
após manter o hub ativo, portanto a política de energia não prova uma cura.

Conclusão: mitigação/diagnóstico instalados, causa raiz ainda não comprovada. Se
persistir em porta direta e noutro sistema, investigar recetor/ligação física e
firmware; mudar definições do compositor não corrige enumeração USB que falha.
Não foi aplicado quirk de kernel arbitrário, atualizada firmware ou mexido no BIOS.

Recuperação: backup.txt indica estado anterior; remover a regra nova e recarregar
udev, restaurar script guardado, e repor os atributos registados em power-before.json.
A regra/diagnóstico constam do código fonte APX; evidência nesta pasta.
Referências: https://docs.kernel.org/driver-api/usb/power-management.html
https://docs.kernel.org/driver-api/usb/error-codes.html
