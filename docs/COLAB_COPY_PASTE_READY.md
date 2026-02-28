# 🚀 COPY-PASTE READY: Colab Setup

## Step 1: Setup (Copy to first Colab cell)

```python
# 🇧🇼 Botswana Political Sentiment Analysis - Quick Setup
print("🚀 Setting up Botswana Political Sentiment Analysis...")

# Install all dependencies
!pip install flask flask-cors transformers torch datasets scikit-learn
!pip install requests beautifulsoup4 lxml pyngrok numpy pandas

# Create project structure
import os
os.makedirs('botswana_sentiment', exist_ok=True)
os.makedirs('botswana_sentiment/data', exist_ok=True)

print("✅ Dependencies installed and project structure created!")
```

## Step 2A: Lexicon Manager (Copy to new cell)

```python
%%writefile botswana_sentiment/lexicon_manager.py
#!/usr/bin/env python3
"""
Setswana Lexicon Manager for Botswana Political Sentiment Analysis
Handles dynamic lexicon expansion, training data collection, and model improvement
"""

import json
import os
import csv
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re

class SetswanaLexiconManager:
    def __init__(self, lexicon_file='data/setswana_lexicon.json'):
        self.lexicon_file = lexicon_file
        self.ensure_data_directory()
        self.lexicon = self.load_lexicon()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs('data', exist_ok=True)
        os.makedirs('data/training_data', exist_ok=True)
        os.makedirs('data/user_contributions', exist_ok=True)
    
    def load_lexicon(self) -> Dict:
        """Load lexicon from file or create default"""
        if os.path.exists(self.lexicon_file):
            try:
                with open(self.lexicon_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading lexicon: {e}, using default")e! 🇧🇼 livl be engine wilt AnalysistimenSenal a PoliticBotswan
Your 
ars! 🎉pe that apL**URngrok the ick ✅
8. **Cl it  cell → Runn finalste i** → PaCopy Step 3it ✅
7. **l → Run n new cel** → Paste i 2Eep6. **Copy Stun it ✅
w cell → Rste in ne2D** → Paopy Step  **C
5. it ✅→ Run new cell  inPasteep 2C** → py St✅
4. **Coun it → Rw cell in ne** → Paste y Step 2BCop. **  
3Run it ✅w cell →  ne → Paste intep 2A**opy S*C *2.n it ✅
Rub cell →  Cola* → Paste inp 1*te. **Copy SNOW:

1T t to do RIGH# 🎯 Wha--

#```

-ad())
p.py').reab_apn('col)
exec(ope.."lask server.🚀 Starting Fint("sk app
prart the Fla St
#timent')
wana_senchdir('botstory
os.direcect ge to proj")

# Chansentimentpi//a_url}blic{pundpoint: "📊 API e)
print(fc_url}"pp: {publiur aaccess yoRL to lick this U🔗 C"rint(f")
public_url}LIVE at: {pour app is (f"🌐 Y0)
print00nect(5 ngrok.conpublic_url =el
e ngrok tunn
# Creatt os
or
impt timeoring
impmport threadok
ingrport  pyngrok im ngrok
fromver with serict the publStaron
# 🌐 

```pythal cell)to finr (Copy ve: Start Ser# Step 3`

#
``False) debug= port=5000,='0.0.0.0',.run(host0)
    app" * 6"=print(    )
    
"n error: {e}ializationit⚠️ Data i(f"rint    p:
    tion as eepxc    except E")
ages in storxisting postred_data)} estond {len(Fount(f"📊     prie:
            elsrd")
    mpty dashboause eiled, will faection ta coll daInitialt("⚠️    prin         else:
             
   ")ed']} postscollect['total_ult_resinitwith {zed nitiali"✅ It(f      prin          ccess'):
sult.get('sut_reif ini            )
sh=Trueefrerce_rta(foand_store_dact_ollee.ctorag_s= datasult it_re        in.")
    ..al datatiting inillec found, cog data No existinnt("🔄  pri     :
     atanot stored_d       if ()
 dataed_age.get_stor_storta = dataored_dast        y:
 tr
   existsf none alize data i Initi #
   
    nalysis") content aicala politor Botswanzed fOptimirint("🇧🇼 ")
    pgration intes ready forPI endpointint("📡 A
    pr)ok URL"ngrable at the il be availlrface wnteeb it("🌐 W    prin=" * 60)
 print("b")
   Google ColaAnalysis on ment tiitical Sen Polg Botswana"🚀 Startint(:
    prin '__main__'==if __name__ emplate)

tring(html_tte_semplar_t rende  return
     '''/html>
 
    <   </body></script>
             }
        );
'_blank's?days=7', icoard/analytdashbi/('/apdow.open      win       () {
   icsn viewAnalytc functio        asyn 
             
   }     }
                    e);
  essag + error.m 'rt('❌ Error:ale                  rror) {
  } catch (e           
     ));ocaleString().toLtampresult.timesw Date( ' + neme:\\n⏰ Ti + 'lt.platformm: ' + resutfor🖥️ Pla '\\nsts +.total_poresultosts: ' + tal p+ '\\n📊 Toult.status + resStatus: ' '✅ alert(                 json();
   e.sponst = await renst resul   co              ;
   health')('/api/ait fetch = awseconst respon                try {
                
    h() {on viewHealtnctiync fu as                 
   }
                    }
      ge);
     messa: ' + error.❌ Erroralert('                 rror) {
   tch (e  } ca          
     ' posts');osts +zed_pnalyresult.ad: ' + ze🧠 Analyosts\\n+ ' pcollected t.total_resulted: ' +  Collec\\n📊essage + '+ result.malert('✅ '           
          );son(.jait responset = aw resul      const      
        ' });POST method: 'raping', {scct/web-('/api/colleit fetchonse = awast resp       con            
  try {         
      () {lectDatanction colasync fu               
     
              }t();
  entimenyzeS   anal            ext;
 ').value = td('textInputlementByIment.getEdocu         
       text) {e(n testExamplnctio         fu      
           }
   
           }           n '#000';
 returfault:    de             757d';
    rn '#6cutral': retu 'ne    case                '#dc3545';
 return negative':      case '    
          45'; '#28a7e': return'positiv    case            
     timent) {itch(sen sw          {
     sentiment) mentColor(ention getSncti    fu              
        }
         ;
 rHTML = htmlnneult').iyId('restB.getElemenentumoc    d       ;
     iv>''</dl +=      htm
                   }
                   
     = '</p>';   html +                 );
   }                span>';
 ype + ')</ entity.t+ ' (' +ntity y.e>' + entit: #28a745""backgrounde=styl"badge" ss== '<span clahtml +                  > {
      h(entity =forEac.entities.xtonteical_colitsult.p          re    ';
       ng>stroties:</cal entirong>Politi<p><sthtml += '                     > 0) {
engtht.entities.lcontexitical_ result.polt &&tical_contexpoliesult. (r   if                
                    }

         /p>';html += '<                 );
           }            an>';
rd + '</sp + wo="badge">' class<spanl += 'tm        h                
ord => {Each(wds_found.forwortswana__analysis.selanguage result.               > ';
    ds:</strongworSetswana <strong> += '<p> html            ) {
        > 0found.lengths_tswana_wordalysis.sege_anuault.langlysis && res_anauagesult.lang      if (re            
           
            `;      sed}</p>
 sult.model_ug> ${re/stronModel:<strong><p><                        }
' : ''></p>trong/sd!<teing detecswitch>🔄 Code-<p><strongetected ? 'switching_dcode_   ${result.             p>
        nguage}</{lastrong> $Language:</<p><strong>               >
         ce)</ponfidenidence}% conf> (${c)}</spanase(UpperCent.to}">${sentiment)ntimtColor(segetSentimenolor: ${"c style=trong> <span/sment:<ntistrong>Se      <p><                 /h4>
 lts:< Resu>📊 Analysis   <h4                     
iment}">lt ${sentss="resuclav  <di                  
 let html = `                
               n';
 e || 'Unknowted_languagt.detec = result language    cons            * 100);
 || 0)ce .confidenesulth.round((re = Matconfidencnst co       ;
         own'unkn 'entiment ||= result.sentiment  const s              
             
          }            return;
                >';
  ror + '</divt.ersul ' + re❌ Error:t">ss="resuldiv claML = '<innerHT).('result'entByIdnt.getElem   docume                 ror) {
 (result.er if        {
        t)t(resululyReson displa    functi        
        
             }   }
         
       ;e + '</div>'rror.messagError: ' + esult">❌ "re'<div class== ).innerHTML ult'('resmentByIdEleett.g    documen               or) {
 errch (at     } c      lt);
     yResult(resupla   dis         );
        son(t response.jsult = awaire const                              
     ;
          })        )
       ext } text: tstringify({ody: JSON.      b       
           },n/json' io': 'applicatntent-Type{ 'Cos:     header                    : 'POST',
odth          me          , {
    i/sentiment''/apfetch(wait nse = aespo rst   con                 y {
          tr          
           div>';
 alyzing...</ Anresult">🔄ass=" '<div clnnerHTML =esult').iById('rentment.getElem        docu       
           }
                     return;
                   t');
  r some texase ente'Plealert(                   trim()) {
 t. (!texif              value;
  ').tInputentById('texetElemument.gt = doctexonst       c      () {
    imentalyzeSentfunction annc asy            cript>
 <s   
          v>
         </di
       </div>     </button>
 alytics>📈 View An"nalytics()ewAick="vig" onclrninclass="wa<button             ton>
    th</butalstem He">❤️ SyiewHealth()"v=o" onclick="infclass <button               utton>
 ata</bect Fresh D🔄 Coll)">ollectData(lick="cuccess" onc"son class=       <butt         ">
griddiv class="           <>
 /h3agement<ata Man    <h3>📊 D">
        containerdiv class=" <
             </div>
   v>
             </di     
 ton>tical</butd Poliixe')">Msetšhabaur molemo for oro e o dira tiple('Masisi testExam" onclick=ton    <but        
    tton>ng</bu-switchideCoho')">ork for batng sentle w is doie('The mmusostExampl"teclick=onon    <butt             l</button>
na Politicaetswa)">SDC2024'na #Uola BotswaC e tla fetela gore UD'Ke dummple(k="testExautton onclic<b            on>
    buttcal</tiish Poli">Engla #BDP2024')for Botswanpromising y looks olicw pBDP\\'s nexample('ck="testElionc<button               
  rid">v class="g       <di  s</h3>
   est Example>🧪 T        <h3ner">
    contaiv class="      <di     
  </div>
        iv>
   /d"><id="result <div       tton>
     </bu Sentimentnalyzeent()">🔍 AlyzeSentimk="anaicbutton oncl <       
    area>"></text" rows="4itching)...code-swor mixed (a, etswannglish, Sxt in Eter te"Enlder=" placeho="textInputrea id      <textah3>
      alysis</ntiment An>🔍 Se <h3           ntainer">
ass="co  <div cl
           div>
           </div>
gle Colab</n Goo>✅ Running os="status"v clas   <di
         t</p>g supporitchinde-swsh coana-EngliSetswsis with nt analyentimeced s <p>Advan           s</h1>
 AnalysiSentimentical na Politotswa<h1>🇧🇼 B            ">
ss="header cla <divy>
          <bod  </head>
 </style>
  
        d; }: bolt-weight45; fonor: #28a7olze: 14px; ct-sion{ ftus         .sta }
             n: 2px;
  argi          mpx; 
      -size: 12        font        12px; 
 der-radius:        bor
        ; white color:               f; 
 #007bfbackground:             
     px;x 8 padding: 4p           ock; 
     inline-bly:la       disp        { 
  adge      .b   x; }
   0p: 1, 1fr)); gap(200px-fit, minmaxautorepeat(s: e-columnrid-templat gplay: grid; { dis    .grid  ; }
      57d#6c7: -left-colororderral { b .neut    }
       3545; r: #dc-cololeftve { border-ti       .nega
     ; }28a745 #color:eft-order-le { btiv.posi                 }
      #007bff;
 : 4px solid -leftder   bor         0; 
     : 15px     margin         s: 8px; 
  iurder-rad      bo          
 20px;    padding:            f8f9fa; 
 ackground: #      b         lt { 
 su   .re         2b8; }
d: #17a backgrounnfo { button.i  }
         ack; color: bl107; fc #fbackground:rning {    button.wa      }
    8a745;ound: #2 backgress { button.succ         px); }
  anslateY(-1trform: 56b3; trans #00ckground:{ batton:hover     bu }
                   : bold;
ont-weight  f           14px;
   t-size: on      f      5px;
       margin:            
  ointer; rsor: p     cu            
px; 6-radius: border               none; 
   border:           0px; 
   ng: 12px 2di   pad        
      white;   color:         ff; 
     7b #00ground:ck       ba    
      tton {      bu   }
        ox;
       border-bzing:  box-si              ze: 14px;
 t-sifon                : 6px; 
adius-rorder        b       
 ecef; x solid #e9border: 2p         0; 
       margin: 8px         ; 
        adding: 12px         p     
   0%;dth: 10          wi      a { 
put, textarein                 }
  1);
     ,0,0,0.x 6px rgba(0adow: 0 4pox-sh          b  x;
    ottom: 20pgin-b         mar      px;
 -radius: 12   border             30px;
 ing:padd          
      ;iteund: wh     backgro         center;
  gn:  text-ali              
  .header {          }
     
        1);0,0,0,0.px rgba(w: 0 4px 6do   box-sha            x 0; 
  15pargin:    m         x; 
    12ps:diu-ra     border     
      5px; ing: 2   padd          
   ite; ckground: wh         ba       r { 
ntaine         .co   }
            00vh;
ht: 1    min-heig            00%);
ba2 1ea 0%, #764eg, #667e35dient(1r-gradneaground: li      back       0px; 
   ing: 2dd       pa
         auto; : 0 argin        m   
      x;0p 90dth:wi max-        
       if; l, sans-seroe UI', Ariay: 'Segt-famil       fon      
    body {       e>
           <styl>
  ="UTF-8"harsetmeta c
        <is</title>lysent Anantimitical Setswana Poltle>🇧🇼 Bo   <ti      <head>
 
  tml>tml>
    <hCTYPE hDO
    <!'late = ''_temp
    htmlting"""tesab r Colface fointermple web   """Si  ome():

def hp.route('/')E ===
@ap INTERFAC
# === WEB }), 500
       
": str(e)  "error   ",
       lthy"unheatatus":      "s
        jsonify({  return      :
on as eeptipt Exc})
    exce              ]
     ics"
 analyt "Advanced             ",
   llectione data coeal-tim      "R        ort",
  ing suppitch   "Code-sw       
      n", y detectiocal entit  "Politi      
        nalysis",nt asentimeEnglish tswana-"Se            [
     eatures":       "f(),
     .isoformatme.now()dateti":  "timestamp         _posts),
  redlen(stol_posts": "tota    ",
        e Colabm": "Googl"platfor     ",
       .0.0-colab"1rsion": "ve          ",
  t Analysiscal Sentimenana Polititsw: "Bo"service"            
",thyheal": ""status         
   nify({n jso retur
       
        data()stored_e.get_ag_stor= dataed_posts  stor     try:
  """
    r Colabeck folth ch"Hea""  lth():
  def hea['GET'])
h', methods=altapi/he'/@app.route(ECK ===
ALTH CH
# === HE 500
str(e)}),error": sonify({"return je:
        ption as  except Exce    })
      or')
     known err', 'Un.get('erroror": resultrr        "e,
        Falsesuccess":    "        
     failed",ction ollea c"Dat": "message               fy({
  jsoniturnre         :
   else
              })      mestamp']
ti: result['imestamp"        "t       0),
  d',nalyzesult.get('a red_posts": "analyze               ted'],
collecotal_result['t: ollected"total_c  "       e,
       Truuccess":      "s    
       ully",essfted succ compleonlectita cole": "Da"messag               fy({
 nisoreturn j           :
 t('success')sult.gef re     i    
     rue)
  _refresh=Tceata(forstore_dct_and_orage.collet = data_st   resul      try:
""
   onment" envirolaba for CCollect dat
    """web_data():t_ollec])
def cPOST' methods=['g',scrapin/web-/api/collectp.route('=
@apOLLECTION == CTA
# === DA(e)}), 500
tror": snify({"errjsoreturn 
        eption as e:xc   except E   })
 
              }  ()
 oformat.ise.now()timte': date    'end_da        
    mat(),).isoforays=days)a(dimedeltme.now() - t (datetiate':  'start_d           ys,
   s': da 'day               riod': {
'pe      
      : analytics,lytics'       'anafy({
     nijsoeturn         r       

 ics(days)alytnced_ant_advagea_storage.cs = dat analyti    =int)
   typeays', 7, t('dest.args.gerequ     days =    :
"
    tryb""or Colaics fanalytd nce"Adva ""s():
   icd_analytardashbo)
def T']['GEods=thytics', mehboard/analapi/dasapp.route('/), 500

@)}str(e": {"errorjsonify(return :
        ception as eexcept Ex   })
    
           }at()
      ().isoformime.nowtet_date': da 'end              ,
 t()formaays)).isoays=d(dtaedelnow() - timatetime.t_date': (d       'star   ays,
        'days': d           : {
   d'      'perio      w_stats,
overvie   'stats':         ({
  jsonifyrnretu     
   
        rview(days)_ove_dashboardge.geta_stora_stats = dat    overviewt)
     7, type=in('days',get.args. request   days =
       try:  a"""
h real datverview witd o""Dashboar"iew():
    rd_overvboa
def dash'])GET methods=['',ieward/overvboe('/api/dash
@app.routDPOINTS ===HBOARD ENDAS }

# ===   )
      str(e"error":            ": False,
ng_detectedswitchi"code_    ",
        sh: "Englianguage""detected_l          0.5,
  idence":       "confl",
      rant": "neutmesenti   "          {
  return     e}")
 s: {alysior in anrrnt(f"E  pri     as e:
  ceptioncept Ex  ex   
        }

       dsor_w": totalount"word_c      ,
      en(text): length"xt_l        "te    hybrid",
b_olaused": "codel_      "m    
           },  rds": []
   "keywo           
   entities,ical_olit ps":tienti         "e     
  {t": al_contexolitic"p   
          },          count
 wana_nt": setsword_coua_an     "setsw
           rds,total_wos": _word"total       
          2),ana_ratio,tswnd(seio": routswana_rat   "se            und,
 words_foana_nd": setswrds_fouwana_wosets     "          sis": {
 analye_ag "langu         ,
  de_switching codetected":_switching_     "codege,
       languauage": d_langecte "det
           ),e, 3fidenc: round(conce"fiden  "con     
     nt,imeent": sentimsent          "n {
  tur  re          

    ntity_type}), 'type': e': entity({'entitypendapies.al_entit     politic        ower:
   ) in text_lr(.loweif entity         tems():
   check.ientities_to_ype in ty, entity_t   for enti   
     
      }      leader'
 do': '', 'Saleshanko': 'leaderer', 'Boisi': 'lead      'Masty',
      ': 'par'BCPty', 'par, 'UDC': ': 'party''BDP           eck = {
 _to_ch  entities    
         lower()
 text.r =   text_lowe    ]
  ties = [ntiical_eit     poln
   tioity detecolitical ent P  #      
   0.5
     ence =       confid
      "neutralent = "sentim    
          else:.1)
      core) * 0ive_score - posit_sgative, 0.6 + (nee = min(0.9  confidenc
          egative"ment = "n   senti      e:
   e_scor positive >oregative_sclif n)
        e) * 0.1orenegative_sc_score - positive (6 +0.9, 0. min(ence =  confid  "
        positivent = "ntime          se_score:
   > negativesitive_score     if po   ntiment
inal seetermine f# D            
   ore += 1
 ive_scat        neg  
      _negative:englishword in     elif         = 1
e +scortive_       posi         ive:
lish_posit in engordif w    
        ords:in wr word 
        fo      ting']
  , 'disappoin'horrible', 'hate', l''awfuible', d', 'terr'ba= [negative english_
        ul']derf'like', 'won 'love', , 'amazing', 'excellent't',eaod', 'gr['gositive = lish_po eng  
     ent boostentimish s    # Engl     
    = 1
   ore +tive_sc   nega                 ive']:
egat'n in lexicon[word         if        :
rdsword in wo      for on:
      lexice' in ativ    if 'neg     
      = 1
 re +sco  positive_         
         tive']:exicon['posid in l      if wor    :
       wordsd in     for worn:
       in lexico 'positive' 
        if       e = 0
 ve_scor  negati     ore = 0
 e_sc    positivalysis
    ntiment anSe    #     
        g = False
itchin  code_sw     "
     ishgle = "En   languag     :
           elseg = True
 _switchin    code      
  nglish"wana-Ege = "Setsngua      la    0.1:
   ratio >etswana_ elif sse
       = Falswitching     code_   na"
     e = "Setswalanguag     
       atio > 0.6: setswana_rif        ge
uatermine lang De       #      
  else 0
   > 0tal_wordsds if to/ total_worana_count setswna_ratio =       setswan(words)
  l_words = leta   to    
       ")
  negative)"{word} (d.append(fds_founna_wortswa          se
      ount += 1 setswana_c          ve']:
     con['negatird in lexion and woe' in lexicf 'negativ      eli")
      )d} (positivef"{wor.append(oundana_words_f     setsw           1
 nt +=_couwana    sets          ve']:
  ['positionicord in lexxicon and witive' in lepos    elif '        pend(word)
_found.apana_wordssw set         
      t += 1etswana_coun     s      ']:
     on_wordsmmicon['co in lex and word' in lexiconn_wordsommo  if 'c    rds:
      n wo word i
        for       ound = []
 ds_fna_wor    setswa = 0
    untana_co       setswower())
 xt.lw+\b', te\l(r'\bndal.fi = re words      ction
  deteLanguage   #     
       exicon
  .lernagon_malexiclexicon =             try:
ple format
imn in slexico   # Get    
 mport re
     i"""
nvironmentlab eysis for Cotiment analified sen""Simpl:
    "e(text)implt_s_texf analyze), 500

de{str(e)}"}ed: alysis fail": f"Anornify({"errturn jso re     as e:
  Exception    except  
   
     fy(result)turn jsoni     re   xt)
ple(teze_text_sim= analyt  resul      ncies)
 ex dependeavoid complab ( Collysis fornaimple a  # S    
      0
    "}), 40videdrotext pr": "No y({"erro jsonif     return       t text:
 no   if     
        
).strip(), ''ext't('t = data.ge   text
     _json().getst= requedata   :
          tryb"""
s for Colasient analyced sentim"""Enhan   ):
 ntiment(lyze_se])
def ana=['POST'ods, methentiment'i/ste('/aprouI ===
@app.YSIS APENT ANALENTIM)

# === Sapp__)
CORS(k(__nameFlasp = )

ap"ded to Colab uploaon files are Pyth sure allake print("M")
   ror: {e} errt"❌ Impo   print(fas e:
 portError  Im")
exceptllycessfuucrted s impoodulesAll mprint("✅ age
    ta_stor daage importa_storm dat
    frole_dataollect_simp import ctorecle_data_collsimpr
    from on_manageort lexicnager impn_ma from lexico:
   
try)
wd()tcend(os.gepath.apps.rts
sympo iforhon path ry to Pytrent directourd c
# Addelta
me, timeport dateti imatetime
from dson jimportimport sys
mport os
 CORS
icors importsk_ng
from flaplate_stri_temernify, rendquest, jsoret Flask, or flask imp"

fromyment
""lab deplogine for Colysis En AnaSentimentical na Politpp
Botswa Asked Flaizab Optim Col""
Googlehon3
"bin/env pyt
#!/usr/p.pyapolab_ntiment/cswana_setefile botthon
%%wril)

```pycelto new y (Cop Colab App Step 2E:
## 
```
orage()leDataSt= Simp_storage tae
datancins storage obal }

# Gl    d data'
   collecterated from tics genege': 'Analy     'messa     
  days", f"{days} od':is_peri  'analys         osts),
 zed': len(palyosts_an'total_p     
          return { 
     
       s'}lysifor anaa available ': 'No datssageurn {'me     ret
       not posts:f 
        i     a()
   datget_stored_sts = self.po
        "" insights"liticalpoor cs fanalytied advanc """Get 
        -> Dict:= 7) int days:self, cs(ced_analytief get_advan    d  }
    
e 0
      s > 0 elspostf total_ ists * 100)/ total_poount itching_ce_sw(cod: age'hing_percentwitcode_s    'c,
        ing_count_switchs': codepost_switching_code          ',
  ountsform_cwn': platkdotform_brea    'pla       
 ge_counts,nguaown': lareakdlanguage_b     '
       unts,coentiment_kdown': sea_brtiment     'sen       s,
tal_poststs': tootal_po    't      urn {
        ret
    1
       + latform, 0)(pounts.get= platform_c[platform] tsm_counplatfor           n')
  'unknowm',atfor('plpost.getplatform =         :
    recent_postsor post in }
        funts = {_co    platform
    downakform breat     # Pl     
   += 1
   unt ing_co code_switch        :
       alse), Fng_detected'itchit('code_swalysis.geif an           
          + 1
   age, 0) et(langus.guntlanguage_coe] = uagounts[langlanguage_c         )
   ish'uage', 'Engled_langt('detects.ge analysi language =         ', {})
  sisnt_analyntimeet('se = post.g  analysis          osts:
recent_ppost in    for  0
     ng_count =witchi  code_s
      counts = {}guage_   lann
     owreakd# Language b             
  
 = 1t] +ts[sentimennt_countime sen              unts:
 nt_contimet in sentimen      if se  tral')
    , 'neuentiment'.get('ss', {})ment_analysitiost.get('senentiment = p s
           ent_posts:recn  post i      for}
  tral': 0e': 0, 'neuiv'negat': 0, ve'positiounts = {iment_c sent    own
   nt breakd # Sentime  
       sts)
      t_pon(recensts = le total_po      stics
 ticulate sta      # Cal     
  t)
   pososts.append(  recent_p          s
     dateinvalids with nclude post# I              pt:
      exce     t)
   s.append(posrecent_post               
     cutoff_date:ate >=  post_d   if           )))
  mat()soforw().i.noetimed_at', datlecte('colpost.geted_at', et('creat.gt(postsoformatetime.fromiate = da      post_d      y:
      tr       sts:
   post in or po        f
        
s = [] recent_post
       (days=days)timedelta) - ow(atetime.n= dte _daoff    cutnge
    by date raposts  # Filter    
            
      }    ge': 0
  ercentahing_pitc   'code_sw        0,
      _posts':hingode_switc       'c  ,
       eakdown': {}platform_br    '       {},
      eakdown':br'language_          
      ,neutral': 0}0, 'ative': ve': 0, 'neg {'positi_breakdown':enttim 'sen              sts': 0,
 al_po      'tot        {
    return         no data
  s if ty statmp e    # Return:
        not posts       if         
 _data()
f.get_stored= sel      posts """
  al datafrom reatistics stt overview   """Ge      Dict:
 ->s: int = 7) lf, dayiew(seboard_overvget_dash  def 
  rn []
        retu        {e}")
 data:tored loading sError "  print(f         
 eption as e:  except Exc
                  ]
rn [ retu            
  
         ata or []ed_dlf._cach   return se             cess'):
'suclt.get(suf re    i  e)
      efresh=Truorce_r(fatand_store_dllect_alt = self.coresu        )
    .."ata.g fresh dlectinound, coltored data fint("No s    pr    some
     lectolists, c data ex no        # If     
      a
     return dat              
       = datad_datahecac._      self           
   d(f)son.loa= j  data                  8') as f:
 oding='utf-, enc, 'r'_file_dataanalyzed open(self. with              _file):
 _dataf.analyzedselsts(exiath.f os.p      i      ile
 fLoad from          #        
  
     taed_da self._cachurn         ret   a:
    ._cached_datf self          ie first
  om cachy to load fr      # Tr:
           try"
   ta""d da analyzeet stored"""G 
       st[Dict]:f) -> Lied_data(selget_stor    def   

  tr(e)}": s "error: False,"success"{     return 
       ata: {e}")_dd_storet_anr in collec(f"Erro      print  as e:
    ception cept Ex
        ex          }
       failed"collection"Data "error": alse, success": F  return {"         :
          else     }
                 format()
 .now().isoetimedat: mestamp""ti               ]),
      p innt_analysis''sentimeif lyzed_posts in anaen([p for p alyzed": l     "an            ts),
   yzed_posnalted": len(alleccotal_    "to             True,
    ": "success              rn {
       retu                    
      ts")
    } posd_posts)alyzeanalyzed {len(nd an Collected a"✅     print(f                    
   
    e.now() datetimtion =olleclf._last_c    se  
          zed_postsly = anad_dataachef._c sel         
      in memorye ach        # C                
 
       e, indent=2)ascii=Falsre_s, f, ensust_pomp(analyzedjson.du            
        :') as fing='utf-8, 'w', encodta_file_dayzedelf.analith open(s         w  a
     d datlyzeana # Save                 
       
        append(post)yzed_posts. anal                  
               }            ': False
  edng_detectode_switchi   'c                    ish',
     Engle': 'anguagdetected_l     '                      0.5,
 ce': nfiden       'co             
        utral',ent': 'neim       'sent                   s'] = {
  ent_analysiim  post['sent                      s
lysi anaoutpost with    # Add                  
   )}: {e}") 'unknown'.get('id',post {osting pnalyzf"Error a  print(                 s e:
     n aptiopt Exce  exce                 
                        d(post)
 appenposts.ed_yz anal                     
                      }
                                alse
ed': Fdetectwitching_ 'code_s                             nglish',
  : 'Euage'lang'detected_                              ': 0.5,
  nce 'confide                           ,
    : 'neutral'iment'     'sent                        = {
   _analysis'] entiment post['s                          
 ysisnal basic a Fallback           #          e:
       ls    e              
      ltent_resuntim= sesis'] analyt_st['sentimenpo                         sult:
   ntiment_re      if se            
                             text'])
 nt(post['e_sentimelyzer.analyzresult = anaiment_nt  se                     nt
 mealyze senti        # An          y:
                tr        
  t['data']:ulresst in  for po       ]
        d_posts = [   analyze          h post
   or eacment fsentilyze  Ana      #     
           
          dent=2)=False, in_asciiensuredata'], f, t['ump(resulson.d         j       s f:
    ) atf-8'coding='u, en'w'_file, lf.data(seith open     w          ata
 aw dSave r    #             
       
         soformat().now().i] = datetimeed_at'ollectt['c        pos       
      + 1['id'] = i     post           
    ['data']):te(resultn enumera, post ior i      f
          nd IDs a timestamps    # Add            ss']:
t['succeif resul      
               )
   simple_data(lect_col =   result         b sources
 ata from we# Collect d                 
    
   .")h data..ting fresllect("🔄 Co  prin       
             }
  hed": True, "cacached data""Using cessage": n {"m   retur               s
  0 minute< 1800:  # 3_seconds() .totalme_diff  if ti          
    llectionlf._last_co se -tetime.now()ff = da     time_di        
   ion:collectst_self._lafresh and _ret forceno  if           utes)
 30 minesh (everyfr to re if we need Check     #:
           try
     it""" and storect new data"""Colle     ict:
   False) -> D: bool = esh_refrf, forceore_data(seld_stllect_anef co   
    d)
 Trueexist_ok=irs('data',    os.maked    "
 "st"oesn't exi if it da directory"Create dat"     "):
   selfy(_directorre_datasuf en  de  
        
Nonetion = lleclast_co   self._
     data = None._cached_        selfctory()
rere_data_disu  self.en   on'
   _posts.jsyzednalle = 'data/azed_data_fiself.analy
        son'ts.jted_poseccollile = 'data/self.data_f):
        __(self_init  def _Storage:
  tas SimpleDazer

clasnaly azer import_analysentimentm rota
fct_simple_daport colleimtor lleccole_data_mpom si
fr Optionalict,st, Dort Lim typing implta
frode timert datetime,atetime impoos
from don
import 
import js""
e app
"r the simplON files fond JSmemory aata in s d
Storeata D MediaSociald r Collectege fota Storaimple Da"""
Sv python3
sr/bin/en
#!/ue.pytorag/data_sna_sentimentefile botswa
%%writ``pythonll)

`cew py to neorage (Co: Data St
## Step 2D)
```
zer(mpleAnalyr = Silyze
anaancenalyzer inst# Global a   }


     itchingcode_sw: ected"itching_det"code_sw            uage,
age": langlangutected_de    "       ce,
 fiden": condence "confi
           ment,ent": sentientim"s      {
           return
    
        0.5= ence      confid"
       eutral"nment =        senti
            else:0.1)
 _score) * sitive poe_score -iv + (negat.9, 0.6 min(0onfidence =        c
    ative"ent = "neg sentim        ore:
   _sctive > posive_scoreif negati    el* 0.1)
    e) ortive_scgae_score - nepositiv0.9, 0.6 + ( = min(denceonfi           cive"
 "positntiment =      se
       _score:e > negativecorpositive_s  if        
     rds)
  .negative_woword in selfs if ordr word in w= sum(1 fotive_score     nega
    e_words)elf.positivrd in srds if wod in wo worum(1 for s_score =ive   positlysis
     entiment ana     # S
   se
        g = Falswitchin   code_         English"
 "language =         se:
           el= True
g witchin      code_s"
      glishana-En = "Setsw language       :
     0.1atio >wana_rf setsli
        eing = False_switchde co           swana"
e = "Setanguag    l    6:
     0.tio >ana_ra    if setsw       
  
    else 0rds > 0if total_woords tal_w_count / to setswana =_ratio  setswana     (words)
 ds = len  total_wor      ana_words)
f.setswrd in selwoin words if rd wor  sum(1 fowana_count =ets   s   tion
  ge detec# Langua   
             ))
ower(text.l\w+\b', '\bre.findall(r   words =      
     re
   rt   impo   """
   t analysismen senti"""Simple     ext):
   , tment(selftize_sen def analy    }
    
     
  ogale'ta', 'b, 'mathaa', 'maswe'osultlhoko', 'b  'bo    
      g',appointin', 'dis', 'horribleful', 'haterrible', 'awbad', 'te          '{
  ords = _wlf.negative    se
    
        
        }otoka'iame', 'bmo', 'sata', 'mole, 'ronate'entle', 'm          'serful',
  e', 'wondlove', 'liking', 't', 'amazxcellen', 'e'greatgood',         'ds = {
    ive_wor.posit selfds
       t wor sentimen    # Simple      
   }
          te'
 'palamenthololo', tiki', 'kge'poloo', a', 'bath'setšhab   'mmuso',        raya',
  , 'dire', 'sa'a', 'nate', 'ratmoko', 'tlho', 'boentlea', 's       'that    'a',
 'o', bo', 'ma', di', ', 'se', '', 'ba''mo', 'goe', , 'la'', 'g        'ke
    rds = {_wowana self.setsrs
       ndicatonguage iswana la   # Set     :
_(self)_init_ _
    defeAnalyzer:ss Simplzer.py
claalyiment_anentnt/swana_sentimee botsil%writefthon
%
```pynew cell)
to  (Copy alyzernt An 2C: Sentime
## Step()
```
mple_datat_all_sillector.coecmple_coll sirntu re"""
   ionta collectsimple daor ion f"Main funct
    ""():_data_simple
def collectr()
llectoDataCoSimplecollector = ple_tor
simollecimple cobal s   }

# Gl   mat()
  .isofortetime.now()stamp': da       'time,
         }        sts)
(mock_poedia': lenial_msoc  'mock_           ,
   sts)n(reddit_po': ledditre       '
         sources': { '
           ,datal_ta': al        'dadata),
    l_ted': len(alotal_collec  't
          ': True,    'success       {
      return       
)
     items"ata)} len(all_dollected: { cal"Totgger.info(f     lo   
 
       ock_posts)nd(mextea. all_data()
       datocial_media_mock_serate_elf.gen= ss    mock_post
     esting) (for tia dataocial med Mock s       # 2.       
 
 ts)osd(reddit_pta.exten all_da
       politics()a_otswanect_reddit_bcoll= self._posts     redditdata)
    (real  posts dit Red      # 1.   

       ta = []_da all       
        .")
on..ecticollta mple datarting si.info("S  logger      ces"""
imple sourll srom aata f"Collect d"   "      Dict:
->lf) ta(sesimple_dallect_all_ def co
    
   postsock_return m
        ia posts") medocialmock sck_posts)} len(moGenerated {o(f" logger.inf
            post)
   osts.append(_pock m     
                 
     })
        ', textdall(r'#\w+ags': re.fin     'hasht       ,
    generator'k_data_ource': 'moc    's           
 ), 30(0,m.randintents': rando       'comm
         50),int(0,  random.randhares':   's            ),
 5, 150int(randm.ndokes': ra'li      
          at(),soform1, 72))).it(m.randinandolta(hours=redew() - tim.no': (datetimed_atreate       'c        1}",
 ser_{i+hor': f"u      'aut
          t,tex'text':          ",
       {i+1}orm}_mock_tf"{pla': f    'post_id      
      latform,': pformlat        'p{
        post =                
 
        'batho')', 'peoplet.replace(= tex       text         er():
     lown text.e' i elif 'peopl         )
      t', 'mmuso'men('governlacetext.rep text =                 er():
   in text.lowgovernment'       if '    
       0.7:m() >andoandom.r    if r
        ge-switchinish codngl-E Setswanasome # Add                  
rms)
      ice(platfodom.chotform = ran      plas):
      ample_posterate(st in enumor i, tex     f     

      tagram']k', 'ins, 'facebooer''twitt= [ms      platfor         

         ]
 #Mining"lhe ba sot setšhatse go thusatshwaneo e     "Meraf        ly",
ana equalBatswenefit all  should benueng rev   "Mini         ,
a #Health"lhokwa thatba bo botetšhaelo jwa s"Boitekan         ntry",
   ss the couroded aceements are noveprare imhc "Healt         ation",
  huta #Educso go itso ya mmuthula ti ba batBaithu          "a",
  tswanreform in Bogent needs urn system The educatio  "     
     irst",aFg #Botswanse di siamen tgotla diphetose baSetšhaba       "
      P2024",s #BColiticwana pas to Bots fresh ideBCP brings   "     ",
     #Parliamentolao o mosha sekaseka manetse goshwe tlamente      "Pa   ",
    elopmenttructure devne infrasn Gaboroe progress i to se"Great          ,
  Jobs"eng #giltlhelaereki ba ba bab thusa wanetse go"Mmuso o tsh          th",
  out #BotswanaYoymenpluth em yoordo more f needs to e government     "Th       i #UDC",
onom a rona a ikthataa ma bua nnete kBoko o        ",
    r nation"o oustability tbrought  has hiprsi's leadeis "Mas        ",
   024 #Changewana #UDC2tola Botsla fe e tgore UDCKe dumela          "4",
   02ture #BDP2fus ana'g for Botswmisinroy looks ppolicc  new economi   "BDP's[
          = mple_posts saana
       h and Setswnglisl posts in Eoliticawana pistic Bots  # Real    
      = []
     mock_posts       ing"""
 r test data foal mediaock sociistic m real"Generate" "      ]:
 st[Dict> Lilf) -dia_data(se_meial_mock_socdef generate    ts
    
pos  return            
 
   {e}")it:g from Reddr collectin"Errorror(f    logger.e     :
   ion as eptexcept Exce
                  
  dit")om Redsts fr popoliticaln(posts)} ollected {le(f"Cgger.info      lo   
      )
         datapost_sts.append(   po                  }
               '')}"
    ermalink', get('pst.m{poddit.co"https://re   'url': f                    wana',
 ddit_r_bots'ree':      'sourc                , 0),
   _comments'numget('t.ents': pos'comm                       0,
 s':     'share                   ,
 ps', 0)('u post.get  'likes':                    mat(),
  ']).isoforutcd_t['create(postimestampetime.fromat': dat'created_                
        ",}nown')unkhor', '.get('autf"u/{post: r'tho      'au            ,
      rip(), '')}".st('selftext'st.getle']}. {po"{post['tit f'text':                        ]}",
t_{post['id'd': f"reddit_i       'pos              
   'reddit',orm': tf    'pla                {
    = ata   post_d                  10:
')) > itle', 'et('tost.gl and len(p_politicais        if             
                )
          
  eywordsf.kn selrd ifor keywo                   ext
 n selft i()rd.lower keywoin title orwer() loword.ey       k          ny(
   itical = a   is_pol                
            ).lower()
 t', ''ext('selftpost.ge= text elf    s           er()
 ').lowe', 'st.get('titl= po  title        
       political if post is  Check      #           
              ['data']
 = itemost          p      ren']:
 ]['childata'ata['d in dor item         f    
   ()
        sonse.ja = respon       dat      
    s()
       for_statuonse.raise_        resp0)
    timeout=1get(url, ession.f.s= selonse   resp       =25"
   itimswana.json?l/Botom/r.reddit.ctps://www "ht     url =      ded
 on neeuthenticati API - no aeddit public     # R
            
       na...")dit r/Botswag from Red"Collectino(ger.inf     log       ry:
     t       
   osts = []
    p     )"""
 JSON APIa (publicwanfrom r/Botssts olitical po"Collect p"   ":
     ct]> List[Diself) -itics(a_polanddit_botswollect_re
    def c    ]
       ente'
 , 'palamhaba'lolo', 'setš'kgethoiki', olotuso', 'p      'mm    ',
  'BokoMasisi', P', ' 'UDC', 'BCP',, 'BDs'ana politicBotsw     ' [
        =lf.keywords    setswana
    ish and Seords in Englcal keyw politina  # Botswa
      ]
              ernment'
  tswanaGov', '#Bocs, '#BWPolitictions'#BotswanaEle       'oko',
     asisi', '#B2024', '#M '#UDC24',cs', '#BDP20swanaPoliti    '#Bot     = [
    shtags_haargetlf.tse    htags
    l hasna politicac Botswacifi specus on # Fo  
         })
           
 '/537.36ppleWebKit) A64n64; xNT 10.0; Wiws indoa/5.0 (Wnt': 'Mozill   'User-Age{
         s.update(n.headerf.sessio     sel
   s.Session()stquession = ref.se     sellf):
   _init__(se   def _lector:
 ColeDataass Simpl)

clger(__name__gging.getLogloger = 
logg.INFO)ogginvel=lfig(leg.basicCon

logginort loggingm
import rando
impimport time
st, Dictt Ling imporfrom typiimedelta
 te,etimmport dat datetime i
fromimport ren
rt jsouests
impoimport req"

APIs
""lex without compc sources ublie pssiblcceocuses on atent
Fical Conana Politfor Botswector ata Collmple D""
Si"ython3
v p/usr/bin/entor.py
#!llece_data_coment/simpltswana_sentiritefile bopython
%%w
```
w cell)to neCopy r (ectota Colltep 2B: Da
## S```

onManager()etswanaLexicager = Sicon_manance
lexster in managicon# Global lex

return total)
        ds+= len(wortotal            
     'metadata':egory != cat         if   ems():
 on.it.lexics in selfory, wordategr c
        fol = 0  tota"
      exicon""rds in ltal wot toCoun""       ") -> int:
 rds(self_total_wodef count
    e
     return Fals       {e}")
     word: ing"Error add    print(f
        e:n as ptiot Exce   excep
             ()
    xiconsave_leelf.eturn s   r            
      ords()
   _total_w= self.countrds'] ]['total_wo['metadata'self.lexicon           at()
 isoformetime.now().dat'] = dated_upast'l'metadata'][on[elf.lexic   s
         te metadata# Upda      
               ry
   rd_entd] = woy][wor[categorf.lexicon sel            
              }
   args
             **kw   
      n'),tioibucontrce', 'user_urt('so.gewargse': k      'sourc          oformat(),
.now().istetime_date': da'added           ,
     ': meaning   'meaning            y = {
  word_entr    
       yntrrd ewo # Create            
         = {}
   ategory] xicon[clf.le      se  :
        xiconself.lein egory not       if cat  
      
          rip()lower().stord. = w  word  y:
          tr"
      con""e lexito thw word d a ne    """Ad     -> bool:
args)r, **kw st meaning:tegory: str,r, caf, word: stel(sef add_word   
    d
        }
        }'}
     turaltext': 'culhy', 'con'philosoptype':  'ubuntu',manity/aning': 'hubotho': {'me     '           },
l'ociaontext': 's'c, lue'e': 'vaypy', 'tharmonl 'sociag': 'meaninsano': {kagi    '         
   al'},nationext': 'cont, 'ymbol', 'type': 's/currency'in 'ra {'meaning':    'pula':            entity'},
'id':  'contextl',tura 'cul 'type':lture',e/cuwana languag: 'Tseaning''metswana': { 's    
           itional'}, 'tradcontext':, 'on''institutitype': s', 'se of chiefg': 'hou'meanin 'ntlo': {          p'},
     leadershi: 't', 'contextional'e': 'tradiefs', 'typaning': 'chiosi': {'me   'dikg           hip'},
  eadersntext': 'ltional', 'co'tradipe': ty, ''chief'meaning': {'kgosi':    '        ce'},
     : 'governanntext''co', 'traditionalp', 'type': chieftainshining': 'ea {'m':'bogosi            nal'},
    atiotext': 'n'conllective', 'type': 'cople', wana peots'Boeaning': ana': {'m    'batsw          al'},
  nation 'xt':', 'conteityident', 'type': 'eniztswana citning': 'Boana': {'mea      'motsw        s
  ermpecific twana-s   # Bots             
ific': {pec 'botswana_s
           },          cial'}
  'soext': or', 'contsect': 'alth', 'typening': 'helo': {'meakaneboite           '     al'},
'soci: ext'ontctor', 'c'see': typ ''education',ng': to': {'meani   'thu      '},
       mic: 'econo'context'ncept', e': 'comy', 'typ: 'econong': {'meanikonomi'     'i        
   mic'},': 'econot', 'contextcepype': 'con, 'tvelopment'ing': 'deeano': {'mgany    'thula       
     },hts': 'rigntext'', 'coconcepte': 'ghts', 'typning': 'ri: {'meanelo'    'ditshwa           '},
 ights: 'rntext''coconcept', pe': 'ty ': 'freedom', {'meaning'ololo':     'tok          
 legal'},': '', 'context': 'concept', 'type'justiceing': ean': {'m 'tshiamelo              al'},
 text': 'legcept', 'con: 'conype': 'law', 'teaning': {'m    'molao'         e'},
    'governanccontext':on', ' 'institutiee', 'type':mmittcil/co: 'counaning'gotla': {'me'lek           
     ecutive'},: 'ex', 'context''positione': r', 'typinisteime mning': 'pr {'mea'tonakgolo':               
 ecutive'},ntext': 'ex'coon',  'positipe':t', 'tyidenng': 'presmeani {'asetilo': 'modul             },
  tic'rademoc ''context':s', ese': 'proc, 'typections'g': 'elmeanin: {'thololo'dikge '               
rnance'},gove'context': ', oncept', 'type': 'crnment' 'rule/govemeaning': {'o':  'pus              nce'},
vernaext': 'got', 'contncep: 'cope' 'tyership',': 'lead{'meaningipele':   'boeteled          '},
    islative': 'legxtion', 'contenstitut': 'it', 'type: 'parliamen{'meaning'ente': alam 'p            c'},
   democrationtext': 'ess', 'c'procpe': ion', 'tyg': 'electeanin'mololo': {th        'kge     
   itical'},xt': 'polt', 'conte: 'concepype'cs', 'tlitipog': 'iniki': {'mean 'polot               ial'},
t': 'soctexve', 'conollecti 'type': 'cple',peog': '': {'meanin     'batho         l'},
   'nationat': 'contexive',: 'collectpe'on', 'tyti 'nang':ba': {'meani   'setšha       
      vernance'},ext': 'gotion', 'contnstitu'ipe':  'tyvernment',ng': 'goaniuso': {'me   'mm           terms
   Political    #           {
   al':  'politic
                  },'}
    ralnext': 'ge', 'conteumity': 'medintenses', 'iltificus/difengeg': 'challeanin': {'mdikgwetlho       '      
   '},ocialt': 's 'contex'high',intensity': 'poverty', 'eaning': ': {'mfalo  'tlhoka              ,
al'}politict': ', 'contexigh' 'very_hensity':'intion', 'oppressaning': elo': {'me'kgatel           '},
     al': 'generxtm', 'conte: 'mediuity'ensrtage', 'intk/sho: 'lac'meaning' { 'tlhaelo':            
   litical'},ext': 'po'cont_high', sity': 'veryinten', 'corruptionng': ' {'meanifere':re      'bofe
          emotion'},t': 'ontex'ch', y': 'higintensit', ''angerng': o': {'meani     'kgalef        ,
   general'}xt': 'ontemedium', 'cntensity': 'roblems', 'i 'p'meaning':ata': {math      '    n'},
      ': 'emotioontext'medium', 'csity': ntename', 'ig': 'shineang': {'mhon     'tl         ion'},
  text': 'emotongh', 'c 'hitensity':inss', 'ing': 'sadneko': {'meanbotlhokutlwelo    '           racter'},
 xt': 'chaconteium', ': 'medty'si 'intenelfishness',eaning': 'sikepo': {'m     'bo        ,
   'general'}ontext': 'c': 'high', intensitye/harsh', '': 'fiercaningle': {'me  'boga            
  '},alt': 'generm', 'contex: 'mediuy'ensitnt', 'i'bad things: g'e': {'meanin      'masw
          neral'}, 'gentext': 'co_high', 'veryensity':intrible', '': 'ter {'meaningfala':     'hutsa        '},
   ': 'generalext, 'cont: 'high'sity', 'intend/evil': 'baeaning'bosula': {'m   '             eral'},
text': 'gen, 'conh''higensity':  'int',ul/bad 'painfmeaning':: {'botlhoko'         '       ment words
e sentiativeg # N              e': {
     'negativ
               },al'}
     litic': 'potextcon, 'y': 'medium'', 'intensitfetyotection/sa': 'prning{'mea': pabalesego           'on'},
     xt': 'emoti'conte: 'high', y'', 'intensitassion 'comp{'meaning':botlhoko': kutlwelo      '  
        '},oliticalontext': 'p'high', 'censity': esty', 'intruth/honning': 'truri': {'mea'boammaa            cal'},
    ': 'politicontext', '': 'high 'intensitye/fairness',ng': 'justic': {'meani    'tshiamo          ,
  cal'}itiol 'p'context':high', y': ', 'intensit': 'peace'meaningo': {''kagis                tical'},
t': 'poli, 'contexmedium'ity': 'e', 'intensrnancvert/good gotional coutradi 'g':'meanin'kgotla': {               '},
 t': 'emotioncontex: 'high', ''intensity'ng': 'joy', aniabo': {'me  'th        },
      motion'context': 'e', 'highensity': ''ints', happines': 'meaningtumelo': {''boi                '},
: 'politicalt'tex, 'cony': 'high'ensiteace', 'intning': 'pso': {'mea 'kgot             neral'},
  ntext': 'ge', 'co'mediumnsity':  'inteng': 'good','meanilemo': {    'mo   
         on'},compariscontext': 'um', '': 'medity', 'intensier 'bettg':eaninka': {'m    'boto         },
   neral'xt': 'ge, 'contem'mediusity': ' 'inten'good/fine',g': : {'meanin'siame'              ,
  on'}'emotitext': igh', 'consity': 'h 'intenappy/glad',aning': 'h': {'meitumelela         ',
       on'} 'emoti'context':gh', 'hiy':  'intensit'love/like',': 'meaningrata': {       '      ral'},
   enetext': 'gconm', '': 'mediutyntensitiful', 'ibeaud/: 'goong'e': {'meanisentl  '            l'},
  'generacontext': m', ': 'mediuensity''intpleasant', nice/ 'ng':niea {'m   'monate':        ords
     entiment wPositive s         #    : {
    sitive'po '        },
               
dium'}': 'meency 'frequl come',ning': 'wil{'meaa':          'tl  m'},
     'mediuequency':  'fr',/shall'willaning':  'ta': {'me              medium'},
  ''frequency':we', eaning': 'ra': {'m           '    m'},
 ediu': 'm'frequency',  'was/were':ingean  'ne': {'m      },
        'high'ency': ve', 'frequ: 'with/haning'mea   'na': {'             h'},
y': 'hig'frequenc'with/by', {'meaning':    'ka':           um'},
   ncy': 'mediueve', 'freqe/giing': 'wher': {'mean       'fa        ium'},
 ency': 'med'frequnot yet',  'still/ {'meaning':':  'sa          
    'medium'},: quency'at', 'fre 'that/e {'meaning':    'la':            'high'},
 equency':'fru', f/yong': 'owa': {'meani     '     
      gh'},ency': 'hi', 'frequg': 'of/goes: {'meanin'ya'          },
      igh': 'hcy'uenect)', 'freqsubj': 'he/she (': {'meaning    'a          
  gh'},y': 'very_hi 'frequenc',: 'he/she/it'meaning'o': {  '         um'},
     y': 'medincequeix', 'fral pref 'plurng':{'meani   'ma':            um'},
  y': 'mediuenc 'freqfix',pretract noun aning': 'abs{'me     'bo':           },
  'high''frequency':l', gs/pluraing': 'thin'mean': { 'di          gh'},
     quency': 'hire'fg', hin 'it/ting':'se': {'mean      
          '}, 'highy':equencple', 'frey/peoaning': 'th'ba': {'me            ,
    ': 'high'}'frequency': 'to/at',  {'meaning':      'go
          h'},y': 'higrequencn/at', 'f: 'i{'meaning'    'mo':           
  ery_high'}, 'vfrequency':th', 'wing': 'and/nile': {'mea  '          igh'},
    very_h 'frequency':t/no', 'ing': 'noean  'ga': {'m            '},
  ry_high': 'verequencyis', 'fI am/it  ''meaning':     'ke': {        words
   a ic Setswan # Bas          ': {
     mmon_words     'co
         },   
       tup']al_se': ['initiources       's    '],
     tems': ['systributor    'con     0,
       ords':   'total_w         t(),
     .isoformaetime.now()d': datast_update     'l           
0',: '1. 'version'               {
ata': tad        'meurn {
         ret
   ext"""l contoliticatswana pcon with Bowana lexiefault Setsed d""Enhanc   "    :
 -> Dictlf) _lexicon(set_defaultdef ge   
    rn False
 tu   re
         e}") {icon:ving lexrror sat(f"E  prin       e:
    xception as    except E   urn True
         ret
    ent=2)=False, indure_asciion, f, enslf.lexicon.dump(se      js     
     ') as f:ing='utf-8 'w', encodile,exicon_flf.lpen(se o    with        try:
      
  e"""n to filve lexico"""Sa
        on(self): save_lexic   
    deficon()
 t_lexdefaulelf.get_rn setu  r
      
        