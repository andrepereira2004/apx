.pragma library
// 30 context groups × 10 introductions × 10 messages = 3000 distinct PT-PT lines.
// Local templates only: no API, network request or background text generation.
var introductions = ["Olá outra vez, André!", "Buu!", "Ora bem.", "Olha quem voltou.", "O fantasma está de serviço.", "Estou por aqui.", "Menu aberto, fantasma presente.", "Olá, André.", "Nada de sustos desta vez.", "Apareci só um bocadinho."];
var groups = {
  "general": [
    "Os botões estão no sítio e eu também.",
    "Podes mexer à vontade; eu fico aqui a fazer companhia.",
    "Uma pausa pequena também conta como progresso.",
    "Há sempre espaço para mais uma boa ideia.",
    "Não tenho pés, mas gosto de manter tudo assente.",
    "O meu grande talento é aparecer quando abres este menu.",
    "Hoje estou com uma transparência exemplar.",
    "Não faço magia, mas encontro os controlos depressa.",
    "Se precisasses de um susto, tinhas aberto outro menu.",
    "Uma coisa de cada vez; até os fantasmas agradecem."
  ],
  "morning": [
    "Bom dia! Vamos dar um arranque tranquilo a isto.",
    "Ainda há um dia inteiro para boas descobertas.",
    "O primeiro clique do dia merece uma receção decente.",
    "A manhã fica melhor com tudo à mão.",
    "Pequeno-almoço primeiro ou mais uma ideia? Tu é que sabes.",
    "Tenho o turno da manhã tratado.",
    "Hoje a inspiração pode chegar antes do café.",
    "Vamos abrir o dia sem pressas desnecessárias.",
    "Uma manhã nova e os mesmos botões de confiança.",
    "Se a cabeça ainda está a arrancar, o menu já está pronto."
  ],
  "afternoon": [
    "Boa tarde! Ainda há muito dia pela frente.",
    "A tarde está a pedir uma mudança de ritmo.",
    "Uma pausa entre tarefas pode saber muito bem.",
    "O turno da tarde também tem companhia fantasmagórica.",
    "Talvez a próxima boa ideia esteja mesmo ao virar do clique.",
    "Já vamos a meio do dia; sem corridas comigo.",
    "Uma coisa pequena terminada já melhora a tarde.",
    "Esta é uma boa altura para esticar um bocadinho as pernas.",
    "A tarde continua e eu guardo-te o lugar no menu.",
    "Vamos escolher o próximo passo com calma."
  ],
  "evening": [
    "Boa noite! O fim do dia também merece bons controlos.",
    "Entrámos no turno em que os fantasmas ficam mais à vontade.",
    "O dia abranda; o menu pode fazer o mesmo.",
    "Uma luz confortável e está montado o serão.",
    "Há serões que começam com uma ideia pequenina.",
    "Tenho a receção do serão aberta.",
    "Pode ser trabalho ou descanso; a companhia está garantida.",
    "O serão não precisa de ser uma corrida.",
    "Esta hora fica bem com um ambiente à tua medida.",
    "Se vier uma boa ideia ao serão, arranjamos-lhe espaço."
  ],
  "night": [
    "A noite chegou e eu continuo por aqui.",
    "Este é, oficialmente, o meu horário favorito.",
    "Um serão tranquilo também é um bom plano.",
    "Os fantasmas têm fama de notívagos; eu só vim ajudar.",
    "À noite, um ecrã confortável faz diferença.",
    "Ainda há espaço para fechar o dia com uma coisa boa.",
    "O menu não faz barulho; combina com esta hora.",
    "Se já estás a abrandar, eu acompanho o ritmo.",
    "A esta hora, até os botões parecem mais sossegados.",
    "Podemos deixar o resto para uma próxima visita."
  ],
  "late": [
    "Já vamos no turno da madrugada.",
    "A madrugada tem ideias curiosas; guarda as boas.",
    "Sou um fantasma, mas também sei apreciar uma pausa.",
    "Se o silêncio inspira, este é um bom cenário.",
    "Um copo de água cabe bem entre duas ideias noturnas.",
    "Há um lado especial nestas horas mais quietas.",
    "O próximo clique pode esperar por um espreguiçar.",
    "Estou a fazer companhia ao turno tardio.",
    "Não precisas de resolver tudo nesta madrugada.",
    "Se o sono aparecer, eu seguro o menu até à próxima."
  ],
  "monday": [
    "Segunda-feira: começamos por uma coisa de cada vez.",
    "Uma segunda-feira não precisa de assustar um fantasma.",
    "A semana pode começar com um passo pequenino.",
    "Ainda temos uma semana inteira para as boas ideias.",
    "Hoje dou especial valor a listas curtas.",
    "Uma tarefa de cada vez também conta à segunda-feira.",
    "Vamos montar a semana sem empilhar demasiadas janelas.",
    "Começar devagar também é começar.",
    "Tenho companhia para este arranque de semana.",
    "A segunda-feira trouxe os seus botões habituais."
  ],
  "friday": [
    "Sexta-feira tem um som muito próprio.",
    "O fim de semana já se aproxima do menu.",
    "Há boas razões para fechar algumas tarefas hoje.",
    "A sexta-feira merece um pequeno momento de satisfação.",
    "Mais uma semana quase do outro lado.",
    "Se hoje houver espaço para lazer, não me oponho.",
    "Este menu funciona igualmente bem em modo sexta-feira.",
    "Podemos pousar algumas preocupações antes do fim de semana.",
    "A reta final da semana também merece calma.",
    "Sexta-feira: uma ocasião respeitável para um sorriso."
  ],
  "weekend": [
    "Fim de semana: o ritmo é teu.",
    "Os fins de semana não precisam de uma lista infinita.",
    "Um projeto só por gosto também merece o seu espaço.",
    "Hoje pode haver mais lugar para experimentar.",
    "Um bocadinho de descanso não estraga plano nenhum.",
    "Estou disponível para as pequenas aventuras do fim de semana.",
    "O menu também sabe trabalhar em modo descontraído.",
    "Se o plano é não ter plano, consigo acompanhar.",
    "Uma boa ideia de fim de semana pode começar aqui.",
    "Lazer também é uma utilização perfeitamente válida deste PC."
  ],
  "minecraft": [
    "Neste Environment, as boas ideias podem vir aos blocos.",
    "Um bloco de cada vez também se aplica aos planos.",
    "Se faltar inspiração, uma construção pequena já serve.",
    "Aqui há espaço para projetos com muitas camadas.",
    "Os creepers ficam no jogo; eu trato só do menu.",
    "Trouxe zero creepers para esta visita.",
    "Uma casa nova pode começar por uma ideia muito simples.",
    "Neste canto do PC, até o planeamento pode ser quadrado.",
    "Inventário mental cheio? Uma pausa ajuda a organizar.",
    "Os blocos podem esperar enquanto ajustas os controlos."
  ],
  "hytale": [
    "O canto do Hytale está preparado para novas aventuras.",
    "Antes de outra aventura, podes acertar o ambiente à tua medida.",
    "Os grandes planos também começam com um pequeno menu.",
    "Uma boa aventura sabe melhor com o som no ponto.",
    "Este fantasma prefere acompanhar a aventura a estragá-la.",
    "Neste Environment, a curiosidade tem bom lugar.",
    "Os controlos ficam aqui à mão para a próxima partida.",
    "Uma pausa entre aventuras não fica mal a ninguém.",
    "Se hoje for dia de explorar, fica o meu voto na curiosidade.",
    "No Hytale, deixo a espada para o ícone e fico pela companhia."
  ],
  "steam": [
    "A biblioteca está por perto; a escolha é tua.",
    "O difícil às vezes é escolher a próxima aventura.",
    "Uma sessão de jogo também merece um ambiente confortável.",
    "Aqui há espaço tanto para descobrir como para repetir favoritos.",
    "Não conto horas de jogo; fico-me pelos botões.",
    "Uma pausa entre partidas é sempre uma hipótese.",
    "O teu próximo jogo pode muito bem ser um velho favorito.",
    "Neste Environment, o lazer tem o seu lugar.",
    "Podes acertar o som antes de escolher a próxima sessão.",
    "Deixo a biblioteca contigo e guardo os controlos."
  ],
  "faculdade": [
    "O cantinho da Faculdade tem companhia.",
    "Uma página de cada vez também faz avançar o trabalho.",
    "Se a matéria se acumular, podemos começar pela mais pequena.",
    "Estudar não exige ter todas as respostas à partida.",
    "Um intervalo curto também cabe num bom plano de estudo.",
    "As ideias costumam gostar de algum espaço entre tarefas.",
    "Não sei a matéria por ti, mas sei onde está o volume.",
    "Uma dúvida bem formulada já é um começo útil.",
    "O objetivo pode ser só avançar um bocadinho hoje.",
    "Até um fantasma respeita uma boa pausa de estudo."
  ],
  "hub": [
    "O Hub é um bom sítio para escolher o próximo destino.",
    "Estamos no ponto de encontro dos teus Environments.",
    "Daqui, podes decidir para que lado segue o dia.",
    "Cada Environment pode ter o seu próprio ambiente.",
    "O centro da casa digital está com a porta aberta.",
    "Os atalhos para os teus espaços continuam por aqui.",
    "Hoje o próximo destino é uma escolha inteiramente tua.",
    "Estou na receção do Hub, com transparência profissional.",
    "Um bom ponto de partida não precisa de fazer barulho.",
    "Há vários cantos neste PC; este é o ponto de encontro."
  ],
  "development": [
    "O espaço de desenvolvimento pede ideias com margem para experimentar.",
    "Um problema pequeno de cada vez é um plano respeitável.",
    "Nem todos os bons projetos começam com uma resposta.",
    "Guardar o que funciona também é progresso.",
    "Os bugs são teus; a companhia é por minha conta.",
    "Uma pausa pode trazer uma perspetiva nova sobre o mesmo problema.",
    "Hoje há espaço para construir qualquer coisa com cuidado.",
    "Um teste que esclarece uma dúvida já tem valor.",
    "Se a ideia crescer, fazemos-lhe espaço no desktop.",
    "O próximo passo pode ser mais simples do que parece."
  ],
  "browser": [
    "Há um navegador aberto; a curiosidade tem por onde seguir.",
    "O mundo cabe mal num separador, mas tentamos.",
    "Mais uma descoberta ou uma pausa nos separadores?",
    "Uma boa página merece um momento de atenção.",
    "Os separadores têm talento para se multiplicar.",
    "Na dúvida, guardar uma página pode ser melhor do que a perder.",
    "Há caminhos que começam só com uma pesquisa.",
    "O navegador está por perto; os controlos ficam aqui.",
    "Uma janela para o mundo também precisa de pausas.",
    "Se encontrares uma coisa interessante, dá-lhe tempo."
  ],
  "terminal": [
    "Há um terminal aberto; o prompt tem companhia.",
    "Uma linha de cada vez também é um ritmo válido.",
    "Os comandos agradecem um segundo olhar antes do Enter.",
    "Neste menu, não precisas de decorar comando nenhum.",
    "O terminal fica com as letras; eu fico com os ícones.",
    "Um prompt aberto tem sempre um ar de possibilidade.",
    "A linha de comandos também merece um ambiente confortável.",
    "Há qualquer coisa de simpático num terminal bem arrumado.",
    "O próximo comando pode esperar por uma pequena pausa.",
    "Se o plano é experimentar, começa pelo passo mais pequeno."
  ],
  "files": [
    "O gestor de ficheiros está aberto; as pastas têm companhia.",
    "Às vezes, arrumar uma pasta já desimpede a cabeça.",
    "Um ficheiro com um nome claro facilita a próxima visita.",
    "Há organização que começa por uma única pasta.",
    "Os ficheiros ficam no seu sítio; eu tento fazer o mesmo.",
    "Um desktop arrumado não precisa de ficar sem personalidade.",
    "Se procuras alguma coisa, uma pasta de cada vez ajuda.",
    "É bom voltar e encontrar as coisas onde as deixámos.",
    "As tuas pastas não precisam de um susto, só de algum espaço.",
    "O próximo grande plano também pode começar num ficheiro pequeno."
  ],
  "music": [
    "Há música em reprodução; eu fico pela companhia silenciosa.",
    "A banda sonora já está escolhida.",
    "Um bom tema muda logo o ambiente do desktop.",
    "Não canto por cima; tenho maneiras.",
    "Se o ritmo está certo, o menu acompanha.",
    "A música trata de uma parte importante do ambiente.",
    "Já temos som para este pedaço do dia.",
    "Deixo o protagonismo para a música.",
    "Uma faixa de cada vez também é um ótimo plano.",
    "O meu instrumento favorito é o silêncio entre os botões."
  ],
  "video": [
    "Há um vídeo em reprodução; prometo uma visita curta.",
    "O ecrã tem sessão marcada.",
    "A imagem fica contigo e os controlos ficam por aqui.",
    "Um vídeo interessante merece que eu não me estique na conversa.",
    "Já há imagens em movimento; eu fico quietinho.",
    "O intervalo é teu, não meu.",
    "Se precisas de acertar o som, chegaste ao sítio certo.",
    "Podemos fazer uma pausa nos controlos e voltar ao vídeo.",
    "Não conto o final de nada; sou um fantasma educado.",
    "Deixo-te voltar à sessão quando quiseres."
  ],
  "many_windows": [
    "Há várias janelas abertas; uma coisa de cada vez ajuda.",
    "O desktop está bem acompanhado hoje.",
    "Tantas janelas e continuo a caber neste cantinho.",
    "Se houver demasiados caminhos, podemos escolher só o próximo.",
    "Um espaço de trabalho cheio também merece alguma ordem.",
    "Não é preciso resolver todas as janelas ao mesmo tempo.",
    "Os workspaces existem para dias com muitos assuntos.",
    "Hoje o teu desktop tem várias frentes abertas.",
    "Às vezes, mudar de workspace já dá uma perspetiva nova.",
    "Um pequeno intervalo entre janelas também serve."
  ],
  "quiet": [
    "O desktop está sossegado; as possibilidades estão em aberto.",
    "Há espaço para começar uma coisa nova.",
    "Uma área de trabalho tranquila também tem o seu encanto.",
    "O primeiro plano do dia ainda pode estar por escolher.",
    "Gosto deste bocadinho antes de se abrirem as janelas.",
    "Poucas janelas, bastante espaço para ideias.",
    "Não é preciso preencher todos os cantos do desktop.",
    "Há dias em que o melhor é começar sem pressa.",
    "O espaço está livre para o que te apetecer fazer.",
    "Um começo calmo combina comigo."
  ],
  "halloween": [
    "Hoje é um dia terrivelmente feliz!",
    "Hoje tenho uma desculpa oficial para aparecer.",
    "É Halloween; o meu turno veio com prestígio extra.",
    "Buu com carinho, que hoje a data ajuda.",
    "Hoje a mascote está perfeitamente enquadrada no calendário.",
    "Os sustos ficam nas histórias; os controlos ficam no sítio.",
    "Hoje estou especialmente à vontade nesta casa digital.",
    "Halloween é o meu equivalente a uma festa de aniversário.",
    "Trouxe espírito de Halloween e zero travessuras nos ficheiros.",
    "Hoje até um fantasma tem direito a sentir-se em casa."
  ],
  "christmas": [
    "Há espírito natalício e, neste caso, um espírito no menu.",
    "Nesta altura, a companhia também conta como presente.",
    "O meu gorro de Natal é invisível, mas a intenção está cá.",
    "Um Natal tranquilo merece um ambiente confortável.",
    "Entre luzes e pausas, também há espaço para este cantinho.",
    "Hoje posso desejar-te boas festas sem sair do desktop.",
    "As prendas ficam contigo; eu guardo os botões.",
    "Trouxe votos de boas festas, não ficheiros embrulhados.",
    "Esta é uma boa altura para dar algum descanso às pressas.",
    "Há pequenos momentos de Natal que cabem num menu."
  ],
  "newyear": [
    "Mais uma volta ao Sol merece uma ideia nova.",
    "O calendário muda; a companhia continua.",
    "Os bons começos não precisam de promessas gigantes.",
    "Uma coisa boa de cada vez já é um belo plano para o ano.",
    "Há espaço para novas ideias neste calendário.",
    "Novo ano, possibilidades em aberto.",
    "O meu desejo para este ano é simples: bons momentos por aqui.",
    "Os fantasmas também sabem apreciar um recomeço.",
    "Que esta volta ao calendário traga descobertas interessantes.",
    "Um ano novo pode começar com um passo pequeno."
  ],
  "freedom_day": [
    "Bom 25 de Abril! Hoje a liberdade merece um lugar no menu.",
    "Hoje há cravos no calendário e liberdade no pensamento.",
    "Um bom 25 de Abril, com espaço para pensar e criar.",
    "Hoje é um bom dia para dar valor à liberdade.",
    "O 25 de Abril também cabe neste pequeno canto do desktop.",
    "Hoje a curiosidade pode passear com um cravo ao lado.",
    "Há datas que merecem uma saudação especial.",
    "Um 25 de Abril tranquilo e cheio de boas ideias.",
    "Hoje deixo-te uma saudação com um cravo imaginário.",
    "Liberdade para escolher o próximo passo: bom 25 de Abril!"
  ],
  "portugal_day": [
    "Bom 10 de Junho! Hoje a saudação vem bem portuguesa.",
    "Hoje o calendário tem um sotaque familiar.",
    "Um bom Dia de Portugal, com tempo para as coisas de que gostas.",
    "Neste 10 de Junho, deixo-te um cumprimento cá da casa.",
    "Hoje há uma data portuguesa à porta deste menu.",
    "Um dia de Portugal com espaço para boas descobertas.",
    "O 10 de Junho merece uma receção em português de Portugal.",
    "Hoje o meu vocabulário trouxe uma saudação especial.",
    "Há pequenos recantos portugueses até dentro do desktop.",
    "Bom feriado, se hoje o puderes aproveitar."
  ],
  "summer": [
    "O verão lembra-me que também há mundo fora do ecrã.",
    "Um ambiente confortável sabe bem nesta altura do ano.",
    "Os planos de verão também podem ter uma pausa digital.",
    "Uma boa ideia pode aparecer entre duas pausas de verão.",
    "Nesta estação, o ritmo pode ser um bocadinho mais leve.",
    "O verão combina com espaço para experimentar.",
    "Um copo de água é uma boa companhia para o desktop.",
    "Há projetos de verão que começam só por curiosidade.",
    "O menu não vai a banhos, mas acompanha os teus planos.",
    "Se houver lugar para descanso, fica a sugestão do fantasma."
  ],
  "winter": [
    "O inverno combina com um cantinho digital confortável.",
    "Há ideias que gostam de serões de inverno.",
    "Um ambiente aconchegado também pode começar pelas cores do desktop.",
    "Nesta estação, apetece-me uma transparência bem confortável.",
    "Os planos de inverno também merecem intervalos.",
    "Um serão sossegado pode dar espaço a uma ideia boa.",
    "Tenho companhia para estes dias de calendário invernal.",
    "O inverno traz outra cadência ao fim do dia.",
    "Podemos dar um bocadinho de cor a este canto do inverno.",
    "Um pequeno conforto entre tarefas também conta."
  ],
  "autumn": [
    "O outono sabe bem a recomeços tranquilos.",
    "Esta estação combina com organizar ideias sem pressa.",
    "Há uma cor de outono que podia ficar bem neste desktop.",
    "O calendário entrou num ritmo diferente; o menu acompanha.",
    "Os serões de outono têm espaço para bons projetos.",
    "Uma ideia nova pode chegar com a mudança da estação.",
    "Gosto de um outono com tempo para curiosidade.",
    "Esta altura do ano combina com pôr algumas coisas em ordem.",
    "O outono trouxe mais uma ocasião para personalizar este cantinho.",
    "Entre recomeços e pequenas pausas, vamos escolhendo o próximo passo."
  ]
};

function eligible(context) {
    var date = context.now || new Date(); var h = date.getHours(); var day = date.getDay();
    var month = date.getMonth() + 1; var dateOfMonth = date.getDate();
    var choices = [{key:"general",weight:2}];
    function add(key,weight) { choices.push({key:key,weight:weight}); }
    add(h >= 6 && h < 12 ? "morning" : h < 18 && h >= 12 ? "afternoon" : h < 22 && h >= 18 ? "evening" : h >= 22 ? "night" : "late",3);
    if (day === 1) add("monday",1); if (day === 5) add("friday",1); if (day === 0 || day === 6) add("weekend",1);
    var env = String(context.environment || "").toLowerCase();
    if (groups[env] && ["minecraft","hytale","steam","faculdade","hub","development"].indexOf(env)>=0) add(env,4);
    if (env === "desenvolvimento") add("development",4);
    var apps = (context.apps || []).join(" ").toLowerCase();
    if (/brave|firefox|chromium|chrome|browser/.test(apps)) add("browser",2);
    if (/kitty|terminal|console|alacritty/.test(apps)) add("terminal",2);
    if (/thunar|nautilus|dolphin/.test(apps)) add("files",2);
    if ((context.count || 0) >= 5) add("many_windows",2);
    if ((context.count || 0) === 0) add("quiet",2);
    if (context.media === "music" || context.media === "video") add(context.media,3);
    if (month === 10 && dateOfMonth === 31) add("halloween",14);
    if (month === 12 && (dateOfMonth === 24 || dateOfMonth === 25)) add("christmas",14);
    if ((month === 1 && dateOfMonth === 1) || (month === 12 && dateOfMonth === 31)) add("newyear",14);
    if (month === 4 && dateOfMonth === 25) add("freedom_day",14);
    if (month === 6 && dateOfMonth === 10) add("portugal_day",14);
    if ([6,7,8].indexOf(month)>=0) add("summer",1);
    if ([12,1,2].indexOf(month)>=0) add("winter",1);
    if ([9,10,11].indexOf(month)>=0) add("autumn",1);
    return choices;
}
function line(key,first,second) {
    return {id:key+":"+first+":"+second,text:introductions[first]+" "+groups[key][second],context:key};
}
function pick(context,recent,random) {
    random = random || Math.random; recent = recent || [];
    var choices=eligible(context); var total=choices.reduce(function(sum,v){return sum+v.weight},0);
    for (var attempt=0;attempt<250;++attempt) {
        var roll=random()*total; var key=choices[0].key;
        for (var i=0;i<choices.length;++i) { roll-=choices[i].weight; if (roll<0) {key=choices[i].key;break;} }
        var value=line(key,Math.floor(random()*10),Math.floor(random()*10));
        if (recent.indexOf(value.id)<0) return value;
    }
    for (var c=0;c<choices.length;++c) for (var a=0;a<10;++a) for (var b=0;b<10;++b) {
        var candidate=line(choices[c].key,a,b); if (recent.indexOf(candidate.id)<0) return candidate;
    }
    return line("general",0,0);
}
function count() { return Object.keys(groups).length * 100; }
