let {MailServices}=ChromeUtils.importESModule("resource:///modules/MailServices.sys.mjs");
let root=MailServices.accounts.localFoldersServer.rootFolder;
if (!root.containsChildNamed("Caixa de entrada")) root.createSubfolder("Caixa de entrada", null);
let folder=root.getChildNamed("Caixa de entrada");
let samples=[
 ["Faculdade", "Materiais para a proxima aula", "Os documentos para a proxima aula ja estao disponiveis.\n\nBom trabalho!"],
 ["Equipa de projeto", "Reuniao de acompanhamento", "Ola!\n\nPodemos reunir na proxima semana para rever o projeto?\n\nObrigado."],
 ["Biblioteca", "A sua reserva esta pronta", "O livro que reservou esta disponivel para levantamento."],
 ["APX", "Uma caixa de entrada mais simples", "Esta e uma mensagem ficticia para testar o novo visual.\n\nO correio da sua conta nao foi usado nesta demonstracao."]
];
if (!folder.getTotalMessages(false)) {
 for(let [i,[name,subject,body]] of samples.entries()) {
  let text="From - Fri Oct 23 10:00:00 2026\r\nX-Mozilla-Status: 0000\r\nX-Mozilla-Status2: 00000000\r\nFrom: "+name+" <preview@example.invalid>\r\nTo: APX Preview <preview@example.invalid>\r\nSubject: "+subject+"\r\nDate: Fri, 23 Oct 2026 "+(12-i)+":00:00 +0100\r\nMessage-ID: <clean"+i+"@example.invalid>\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n"+btoa(body)+"\r\n\r\n";
  folder.QueryInterface(Ci.nsIMsgLocalMailFolder).addMessage(text);
 }
}
let a=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail").currentAbout3Pane;
a.displayFolder(folder);
return true;
