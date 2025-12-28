\NeedsTeXFormat{LaTeX2e}\relax
\ProvidesClass{SimSemBericht}

% KomaScript-Klasse mit den elementarsten Optionen laden.
\LoadClass[oneside]{scrarticle}
\KOMAoption{fontsize}{11bp}
\KOMAoption{DIV}{10}
\KOMAoption{headings}{normal}
\KOMAoption{usegeometry}{on}
\KOMAoption{numbers}{noendperiod}
\DeclareTOCEntryStyle{undottedtocline}

% Absätze mit etwas Abstand und etwas größerer Zeilenabstand.
\RequirePackage{setspace}
\setparsizes{1em}{\medskipamount}{0pt plus 1fil}
\setstretch{1.3}
\setlength{\parindent}{0pt} % Einschub bei Absatz auf 0

% Damit das Paket listings richtig funktioniert
\RequirePackage{scrhack}

% Allgemeine Geometrie
\RequirePackage{geometry}
\setlength{\footheight}{20pt}
\geometry{paper=a4paper,
          left=3cm, right=3cm,
          top=1in, bottom=1in,
          headheight=18pt}

% Schrift, Sprache und Encoding
\RequirePackage[ngerman]{babel}
\RequirePackage{iftex}
\ifLuaTeX
   \RequirePackage[math-style=TeX,
                   bold-style=ISO,
                   partial=upright]{unicode-math}
   \RequirePackage{fontspec}
   \RequirePackage{microtype}
   \defaultfontfeatures{Ligatures=TeX}
   \setmainfont[Scale=1.00]{Erewhon}
   \setsansfont[Scale=0.90]{Nimbus Sans L}
   \setmonofont[Scale=0.95]{Source Code Pro}
   \setmathfont[Scale=1.00, CharacterVariant=3]{Erewhon Math}
   \renewcommand{\vec}{\rightharpoonaccent} 	
   \renewcommand{\Box}{\mdlgwhtsquare}
   \renewcommand{\leadsto}{\rightcurvedarrow}
   \RequirePackage{newunicodechar}
   % Ersetze das Symbol Ohm durch das normale Omega.
   \newunicodechar{^^^^2126}{^^^^03a9}
\else
   \RequirePackage[utf8]{inputenc}
   \RequirePackage[T1]{fontenc}
   \RequirePackage{microtype}
   \RequirePackage{erewhon}
   \usepackage[utopia,vvarbb]{newtxmath}
   \RequirePackage{tgheros}
   \RequirePackage[ttdefault, scale=0.95]{sourcecodepro}
   \DisableLigatures{encoding=*, family=tt*}
   \RequirePackage{amsfonts}
   \newcommand{\symbf}{\boldsymbol}
\fi


% Gleichungsnumerierung mit Kapitel.FortlaufendeNumme
\RequirePackage{amsmath}

% Einheiten richtig setzen: c=\qty{3e8}{km/s} oder \unit{kV}
\RequirePackage{siunitx} 
\sisetup{locale = DE}

% Mövchen anstelle von Anführungszeichen verwenden.
\renewcommand{\glqq}{\frqq}
\renewcommand{\grqq}{\flqq}

% Formatierung von urls. Diese werden aber in der normalen Laufschrift gesetzt.
\RequirePackage{url}
\urlstyle{same}

% Grafiken
\RequirePackage{graphicx}

% Kopfzeilen und Seitennumerierung
% Im einseitigen Satz gibt es nur rechte, ungerade Seiten!
\RequirePackage[automark]{scrlayer-scrpage}
\lohead[]{\slshape \leftmark}
\cohead[]{}
\rohead[]{\upshape \pagemark}
\lofoot[]{}
\cofoot[]{}
\rofoot[]{}
\KOMAoption{headsepline}{0.5pt}

% Haengende Fussnoten
\deffootnote[2em]{2em}{0pt}{\textsuperscript{\thefootnotemark}~}

% paragraph und subparagraph genauso behandeln, wie section und
% subsection. Das heißt: Neue Zeile anfangen und diese nicht einrücken.
\RedeclareSectionCommands[
   runin=false,
   afterindent=false,
   afterskip=1sp]{paragraph, subparagraph}

% Schöne Tabellen
\RequirePackage{booktabs}

% Anklickbare Querverweise im PDF
\RequirePackage{hyperref}
\hypersetup{hidelinks}

% Formatierung der Figure- und Table-Captions
%\floatplacement{table}{tbp}
%\floatplacement{figure}{tbp}
\setlength{\abovecaptionskip}{8pt}
\setlength{\belowcaptionskip}{0pt}
\KOMAoption{captions}{tableheading}
\KOMAoption{captions}{belowfigure}
\KOMAoption{captions}{oneline}
\KOMAoption{captions}{bottombeside}
\KOMAoption{captions}{outerbeside}
\renewcaptionname{ngerman}{\figurename}{Abb.}
\renewcaptionname{ngerman}{\tablename}{Tab.}
\setkomafont{captionlabel}{\small\itshape\bfseries}
\setkomafont{caption}{\small\itshape}
\setcapindent{0pt}


% Seiten duerfen eine variable Laenge haben.
\raggedbottom

% Werte für die Platzierung von Float-Objekten
\renewcommand*{\floatpagefraction}{.90}% min. 90% float on float pages
\renewcommand*{\textfraction}{.15}     % min. 15% text on non-float pages
\renewcommand*{\topfraction}{.85}      % max. 85% floats top
\renewcommand*{\bottomfraction}{.85}   % max. 85% floats bottom
\setcounter{topnumber}{1}              % max. 1 float top
\setcounter{bottomnumber}{1}           % max. 1 float bottom
\setcounter{totalnumber}{3}            % max. 3 floats per page

% Abstand Interpuktionen in abgesetzten Gleichungen
\newcommand{\eqip}[1]{\ #1}

% Definiere die Titelzeile mit dem Ohmlogo
\RequirePackage{xcolor}
\newcommand{\@Ohm@Title}{%
  \begingroup%
  \definecolor{RedOhm}{RGB}{199, 36, 38}
  \setlength\tabcolsep{0pt}%
  \sffamily%
  \raisebox{-1mm}{\includegraphics[scale=1.0]{SimSemBerichtLogo}}
  \color{RedOhm}\hfill%
  \begin{tabular}[b]{ll}
    Fakultät Angewandte Mathematik, \\
    Physik und Allgemeinwissenschaften
  \end{tabular}%
  \endgroup%
}

% Gestaltung des Titelblatts
\renewcommand*{\maketitle}{%
  \begin{titlepage}
    \noindent\@Ohm@Title
    \begin{center}
      \vfill
      \sffamily
      \huge \textbf{Projektbericht} \par
      \huge \textbf{\@title} \par \@subtitle \par
      \vspace*{1cm}
      \Large \begin{tabular}[t]{c} \@author \end{tabular} \par
      \vspace*{1cm}
      \large \@date \par
      \vfill\vfill
    \end{center}
    \thispagestyle{empty}
  \end{titlepage}}

\endinput


