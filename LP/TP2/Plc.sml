(* Plc interpreter main file *)

fun run (e:expr) = 
    let
        val eType  = teval e []
        val eValue = eval  e []
    in
        (val2string eValue) ^ " : " ^ (type2string eType)
    end
    handle SymbolNotFound => "PlcChecker: A expressao contem simbolos nao definidos."
        | EmptySeq => "PlcChecker: sequência vazia."
        | UnknownType => "PlcChecker: tipo usado nao reconhecido."
        | NotEqTypes => "PlcChecker: só sao permitidas comparações entre elementos de mesmo tipo."
        | WrongRetType => "PlcChecker: retorno de funçao nao compatível com corpo."
        | DiffBrTypes => "PlcChecker: tipos de retorno diferentes em um mesmo branch."
        | IfCondNotBool => "PlcChecker: if com condicional nao booleana."
        | NoMatchResults => "PlcChecker: nao foi possível realizar o match da expressao."
        | MatchResTypeDiff => "PlcChecker: match tem tipos diferentes."
        | MatchCondTypesDiff => "PlcChecker: o tipo de uma expressao difere da expressao inserida para match."
        | CallTypeMisM => "PlcChecker: tipo do parâmetro recebido nao corresponde com o parâmetro esperado."
        | NotFunc => "PlcChecker: chamando valor que nao e uma funçao."
        | ListOutOfRange => "PlcChecker: acessando valor alem do escopo da lista."
        | OpNonList => "PlcChecker: tentando acessar um valor que nao e uma lista."
        | Impossible => "PlcChecker: essa açao nao e possivel."
        | HDEmptySeq => "PlcChecker: sequencia vazia, nao e possivel acessar a cabeça."
        | TLEmptySeq => "PlcChecker: sequencia vazia, nao e possivel acessar a calda."
        | ValueNotFoundInMatch => "PlcChecker: nao foi possivel achar um match na lista de matchs."
        | NotAFunc => "PlcChecker: chamando valor que nao e uma funçao."
        | _ => "PlcChecker: erro desconhecido."