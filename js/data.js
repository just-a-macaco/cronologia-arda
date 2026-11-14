/* Dati della timeline. Un unico dataset che alimenterà anche mappe e alberi.
   Schema evento: {id, era, year (numerico, per la posizione sul cerchio), approx,
   label (testo visibile), title, desc, type, place, people, source}.
   Date attualmente da memoria: DA VERIFICARE contro l'Appendice B (Il Signore degli
   Anelli) prima della pubblicazione. Le descrizioni sono in parole proprie. */

const ERAS=[
  {id:"terza",name:"Terza Era",len:3021}
];

const EVENTS=[
  {id:"arnor-gondor",era:"terza",year:1,label:"Anno 1",title:"Nascono Arnor e Gondor",type:"fondazione",
   desc:"Dopo la sconfitta di Sauron, Isildur e Anárion fondano i due regni dei Dúnedain in esilio: il regno del Nord e quello del Sud."},
  {id:"isildur-anello",era:"terza",year:2,label:"Anno 2",title:"Isildur e l'Anello",type:"perdita",
   desc:"Isildur, che aveva rifiutato di distruggere l'Unico, muore in un agguato presso i Campi Gladden: l'Anello sprofonda nell'Anduin."},
  {id:"istari",era:"terza",year:1000,approx:true,label:"Anno 1000 circa",title:"Giungono gli Istari",type:"evento",
   desc:"Nell'ansia per l'Ombra che cresce in Oriente, giungono in Terra di Mezzo i cinque Maghi: fra essi Gandalf e Saruman."},
  {id:"dol-guldur",era:"terza",year:1050,approx:true,label:"Anno 1050 circa",title:"Sauron occupa Dol Guldur",type:"evento",
   desc:"L'Ombra cala sul Bosco Verde, che da allora è chiamato Bosco Atro. Nessuno sa ancora chi vi si nasconda."},
  {id:"angmar",era:"terza",year:1300,approx:true,label:"Anno 1300 circa",title:"Il Re Stregone fonda Angmar",type:"fondazione",
   desc:"Il capo dei Nazgûl riappare a nord e fonda il regno di Angmar, dichiarando guerra ai Dúnedain del Nord."},
  {id:"grande-peste",era:"terza",year:1636,label:"Anno 1636",title:"La Grande Peste",type:"distruzione",
   desc:"Un'epidemia devastante spopola la Contea e uccide gran parte della popolazione di Gondor. Il regno del Sud non si riprenderà mai del tutto."},
  {id:"battaglia-campo",era:"terza",year:1944,label:"Anno 1944",title:"Battaglia del Campo",type:"battaglia",
   desc:"Gli Auriga d'Oriente travolgono l'esercito di Gondor e uccidono il re Ondoher. È il generale Eärnil a riportare l'ultima grande vittoria del Sud."},
  {id:"battaglia-fornost",era:"terza",year:1975,label:"Anno 1975",title:"Battaglia di Fornost",type:"battaglia",
   desc:"Un esercito di Gondor sbarcato nel Nord sconfigge il Re Stregone davanti alle rovine di Fornost. Il regno di Arnor non si rialza più."},
  {id:"earnur",era:"terza",year:2050,label:"Anno 2050",title:"Sparisce Eärnur",type:"perdita",
   desc:"L'ultimo re di Gondor accetta la sfida del Re Stregone e non fa più ritorno. Da allora i Steward governano, in attesa di un re che non torna."},
  {id:"sauron-ritorno",era:"terza",year:2460,label:"Anno 2460",title:"Sauron torna a Dol Guldur",type:"evento",
   desc:"Dopo secoli di silenzio, l'Ombroso vi fa ritorno con forza rinnovata."},
  {id:"gollum-anello",era:"terza",year:2470,approx:true,label:"Anno 2470 circa",title:"L'Anello ritrova un padrone",type:"evento",
   desc:"Sméagol uccide l'amico Déagol presso l'Anduin, si impadronisce dell'Anello e si nasconde sotto le Montagne Nebbiose: nasce Gollum."},
  {id:"rohan",era:"terza",year:2510,label:"Anno 2510",title:"Nasce Rohan",type:"fondazione",
   desc:"Gli Auriga giungono alle porte di Gondor: gli uomini di Éorl li sbaragliano ai Campi del Celebrant e ricevono in dono la pianura di Calenardhon."},
  {id:"lungo-inverno",era:"terza",year:2758,label:"Anno 2758",title:"Il Lungo Inverno",type:"distruzione",
   desc:"Neve senza precedenti e un'invasione da sud-ovest mettono in ginocchio Rohan: il re Helm muore nella fortezza di Hornburg."},
  {id:"guerra-nani",era:"terza",year:2799,label:"Anno 2799",title:"Fine della guerra dei Nani",type:"battaglia",
   desc:"Dopo anni di guerra vendicativa per la morte di Thrór, i Nani sconfiggono gli Orchi alla battaglia di Azanulbizar, alle porte di Moria."},
  {id:"smaug-cinque-eserciti",era:"terza",year:2941,label:"Anno 2941",title:"Smaug cade, e i Cinque Eserciti",type:"battaglia",
   desc:"Un drago, un nano, un mago e un hobbista: la morte di Smaug e la battaglia dei Cinque Eserciti riequilibrano il nord della Terra di Mezzo."},
  {id:"sauron-si-dichiara",era:"terza",year:2951,label:"Anno 2951",title:"Sauron si dichiara",type:"evento",
   desc:"L'Ombroso torna a Dol Guldur e si proclama apertamente: manda tre Nazgûl lungo l'Anduin a cercare l'Anello."},
  {id:"frodo-parte",era:"terza",year:3018.72,label:"23 settembre 3018",title:"Frodo lascia la Contea",type:"evento",
   desc:"Inizia la devastante traversata della Terra di Mezzo che porterà l'Anello a sud."},
  {id:"gandalf-moria",era:"terza",year:3019.04,label:"15 gennaio 3019",title:"Gandalf cade a Moria",type:"perdita",
   desc:"Sul Ponte di Khazad-dûm il mago affronta il flagello di Durin per permettere alla Compagnia di fuggire."},
  {id:"pelennor",era:"terza",year:3019.2,label:"15 marzo 3019",title:"Battaglia dei Campi del Pelennor",type:"battaglia",
   desc:"Minas Tirith è all'assedio quando arriva Rohan: la più grande battaglia della Terza Era si svolge sotto le mura della città."},
  {id:"distruzione-anello",era:"terza",year:3019.27,label:"25 marzo 3019",title:"Distruzione dell'Anello",type:"distruzione",
   desc:"Ai piedi del Monte Fato la missione si compie: Gollum, l'Anello e il fuoco chiudono insieme la storia dell'Unico."},
  {id:"porti-grigi",era:"terza",year:3021.75,label:"29 settembre 3021",title:"Partenza dai Porti Grigi",type:"evento",
   desc:"Frodo, Bilbo e gli ultimi portatori dell'Anello salpano verso l'Occidente: finisce la Terza Era."}
];
