# LocalSend: ligação limitada ao iPhone no piloto APX

Estado: instalado no piloto e validado parcialmente em 2026-10-15. Não altera
a arquitetura de produção APX; transferência real depende de validação no iPhone.

O proprietário forneceu o peer 192.168.1.100. A Faculdade usa rede privada/NAT;
o filtro original impede LAN. O endpoint local LocalSend funciona com TLS e
certificado de cliente (mTLS); a ausência desse certificado explica o ensaio
anterior falhado. Avisos do plugin NetworkManager não impedem esse endpoint.
Não instalar outro gestor de rede nem corrigir o binário sem necessidade.

## Contrato

- Configuração Host-owned, modo 0600, sem symlinks, num diretório privado:
  /var/lib/apx/localsend-network-v1/config.json. Contém apenas schema, environment,
  generation UUID, peer IPv4 e enabled. IP limita a rede; não autentica a pessoa.
- Apenas o Environment gráfico ativo, com registo da mesma geração, unidade
  ativa, máquina nspawn e interface correspondente, recebe a exceção.
- Peer deve estar na LAN física atual, numa interface física, sem ser endereço
  local, gateway, rede, broadcast ou endereço APX. Sem saída para siblings.
- Permitir só TCP LocalSend 53317 para esse peer. Para responder a uma ligação
  de receção, permitir só conexões estabelecidas com origem TCP 53317.
- Receção: DNAT só de peer→IP físico atual do Host:53317 para o IP privado
  atual do Environment:53317, apenas pela interface física selecionada.
  Não abrir porta de entrada genérica no Host. Não retransmitir multicast.
- Todas as regras vivem na tabela nft original da geração; o teardown APX já
  elimina essa tabela. O reconciliador não cria tabelas de Environments.
- Uma chain própria, chamada antes dos bloqueios originais, aceita somente os
  fluxos especificados. Desativar/falhar validação esvazia a chain e remove DNAT;
  o salto vazio não concede acesso e desaparece no teardown normal. Uma regra de
  receção nega TCP 53317 após o salto, para bloquear também conexões com DNAT
  antigo ainda em conntrack quando as permissões forem revogadas.
- Serviço reconciliador a cada 5 segundos atualiza DHCP do Host/Environment; configuração permanece
  ligada à geração selecionada. Em condições inválidas, remover a exceção na
  próxima execução; o encerramento normal remove-a imediatamente pela tabela.
- Unidade com ExecStopPost revoga exceções próprias. Não modifica documentos,
  emparelhamentos, gestão Wi-Fi ou serviços dentro dos Environments.

## Utilização e limites

Sem multicast, usar envio manual para o IP do peer e favoritos LocalSend.
No iPhone, o endereço de receção é o IP Wi-Fi atual do computador, não o IP
privado da Faculdade. Receção exige aceitação manual; não ativar quick-save.
A exceção de IP fica guardada, mas uma mudança do IP do iPhone exige atualização;
uma reserva DHCP no router reduz essas mudanças. Descoberta automática em redes novas continua trabalho separado. O toggle de
criação está instalado: módulo iphone-integration, desligado em todos os presets,
incluindo Completo. Instala LocalSend/Ayatana sem copiar credenciais ou conceder
LAN. A ligação a um dispositivo tem de ser configurada para o novo Environment.

## Recuperação e validação

Backup dos artefactos adicionados e inventário em
/var/lib/apx/backups/20261015-localsend-network. Para reverter, desativar e
parar serviço (revoga regras) e remover só os ficheiros novos registados. Não
restaurar home nem mexer nos filtros originais. Em caso de dúvida, invocar o
helper com --revoke, que não depende de configuração válida.

Testes devem cobrir validação de identidade, LAN/endereços proibidos, renderização
das regras, revogação em falha e comportamento inerte sem opt-in. Validação física:
nft -c, APIs mTLS nos dois sentidos, ausência de acesso genérico à LAN e estado
das regras; transferências reais dependem do iPhone aberto e aceitação do dono.

## Evidência de instalação

29 testes focados passaram (12 rede LocalSend, 4 isolamento existente, 9 catálogo
e 4 defaults), assim como validação de unidade e catálogo/presets JavaScript.
Manifesto Host-owned do LocalSend é admitido pelo resolver e tem hash válido.
Stop/re-enable removeu/recriou permissões e DNAT; guard de receção permaneceu.
Não houve round trip de Environment nem criação real de um novo Environment.

Favorito Tomate Fixe guardado dentro da Faculdade com IP e fingerprint observada.
Backup das preferências permanece no mesmo home, em
~/.local/state/apx-localsend-network-v1/preferences-before-20261015.json; não
exportar esse ficheiro, pois inclui a identidade privada da própria app. Nenhuma
chave pessoal copiada para Host/Hub ou irmãos. Identidade descartável do teste
mTLS eliminada após uso. Aceitação manual de ficheiros permanece inalterada.

O iPhone respondeu inicialmente à consulta feita pelo Host. Quando a exceção
ficou pronta, já não escutava na porta 53317; isso também ocorreu no Host, sem
passar pelo filtro APX. Não atribuir essa indisponibilidade à APX nem declarar
Faculdade→iPhone ou receção física funcionais sem novo teste.

Menu e seeds atualizados com cópias anteriores em
/var/lib/apx/backups/20261015T083722Z-localsend-creation. Fonte e runtime instalado
têm hashes novos do shell e admitem localsend-bin-v1.json. Artefacto local validado;
não foi criado um Environment só para validar instalação completa.
