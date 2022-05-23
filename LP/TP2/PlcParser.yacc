%%

%name PlcParser

%pos int

%term VAR
    | FUN | REC | COLON
    | IF | THEN | ELSE
    | MATCH | WITH
    | EXCLAMARK | HD | TL | ISE
    | PRINT | AND| PLUS | MINUS | MULTI 
    | DIV | EQUAL | DIFF | LESS | LESSEQUAL
    | DOUBLECOLON | SEMICOLON
    | ESQCOLCH | DIRCOLCH
    | ESQPAREN | DIRPAREN 
    | ESQCHAVE | DIRCHAVE
    | FN | ASSIGN | END
    | TRUE | FALSE
    | COMMA
    | NAT of int
    | BAR | ARROW
    | DASH
    | NIL | BOOL | INT
    | NAME of string
    | EOF

%nonterm Prog of expr
  | Decl of expr
  | Expr of expr
  | AtomExpr of expr
  | AppExpr of expr
  | Const of expr
  | Comps of expr list
  | MatchExpr of (expr option * expr) list
  | CondExpr of expr option
  | Args of (plcType * string) list
  | Params of (plcType * string) list
  | TypedVar of plcType * string
  | Type of plcType
  | AtomType of plcType
  | Types of plcType list

%right SEMICOLON ARROW
%nonassoc IF
%left ELSE
%left AND
%left EQUAL DIFF
%left LESS LESSEQUAL
%right DOUBLECOLON
%left PLUS MINUS
%left MULTI DIV
%nonassoc EXCLAMARK HD TL ISE PRINT
%left ESQCOLCH

%eop EOF

%noshift EOF

%start Prog

%%

Prog: Expr (Expr) 
    | Decl (Decl)

Decl: VAR NAME EQUAL Expr SEMICOLON Prog (Let(NAME, Expr, Prog))
    | FUN NAME Args EQUAL Expr SEMICOLON Prog (Let(NAME, makeAnon(Args, Expr), Prog))
    | FUN REC NAME Args COLON Type EQUAL Expr SEMICOLON Prog (makeFun(NAME, Args, Type, Expr, Prog))

Expr: AtomExpr(AtomExpr)
    | AppExpr(AppExpr)
    | IF Expr THEN Expr ELSE Expr (If(Expr1, Expr2, Expr3))
    | MATCH Expr WITH MatchExpr (Match(Expr, MatchExpr))
    | EXCLAMARK Expr (Prim1("!", Expr))
    | Expr AND Expr (Prim2("&&", Expr1, Expr2))
    | HD Expr (Prim1("hd", Expr))
    | TL Expr (Prim1("tl", Expr))
    | ISE Expr (Prim1("ise", Expr))
    | PRINT Expr (Prim1("print", Expr))
    | Expr PLUS Expr (Prim2("+", Expr1, Expr2))
    | Expr MINUS Expr (Prim2("-", Expr1, Expr2))
    | Expr MULTI Expr (Prim2("*", Expr1, Expr2))
    | Expr DIV Expr (Prim2("/", Expr1, Expr2))
    | MINUS Expr (Prim1("-", Expr))
    | Expr EQUAL Expr (Prim2("=", Expr1, Expr2))
    | Expr DIFF Expr (Prim2("!=", Expr1, Expr2))
    | Expr LESS Expr (Prim2("<", Expr1, Expr2))
    | Expr LESSEQUAL Expr (Prim2("<=", Expr1, Expr2))
    | Expr DOUBLECOLON Expr (Prim2("::", Expr1, Expr2))
    | Expr SEMICOLON Expr (Prim2(";", Expr1, Expr2))
    | Expr ESQCOLCH NAT DIRCOLCH (Item(NAT, Expr))

AtomExpr: Const (Const)
    | NAME (Var(NAME))
    | ESQCHAVE Prog DIRCHAVE (Prog)
    | ESQPAREN Comps DIRPAREN (List(Comps))
    | ESQPAREN Expr DIRPAREN (Expr)
    | FN Args ASSIGN Expr END (makeAnon(Args, Expr))

AppExpr: AtomExpr AtomExpr (Call(AtomExpr1, AtomExpr2))
    | AppExpr AtomExpr (Call(AppExpr, AtomExpr))

Const: TRUE (ConB true) | FALSE (ConB false)
    | NAT (ConI(NAT))
    | ESQPAREN DIRPAREN (List [])
    | ESQPAREN Type ESQCOLCH DIRCOLCH DIRPAREN (ESeq(Type))

Comps: Expr COMMA Expr (Expr1::Expr2::[])
    | Expr COMMA Comps (Expr::Comps)

MatchExpr: END ([])
    | BAR CondExpr ARROW Expr MatchExpr ((CondExpr, Expr)::MatchExpr)

CondExpr: DASH (NONE)
    | Expr (SOME Expr)

Args: ESQPAREN DIRPAREN ([])
    | ESQPAREN Params DIRPAREN (Params)
    
Params: TypedVar (TypedVar::[])
    | TypedVar COMMA Params (TypedVar::Params)

TypedVar: Type NAME ((Type, NAME))

Type: AtomType (AtomType)
    | ESQPAREN Types DIRPAREN (ListT(Types))
    | ESQCOLCH Type DIRCOLCH (SeqT(Type))
    | Type ARROW Type (FunT (Type1, Type2))

AtomType: NIL (ListT [])
    | BOOL (BoolT)
    | INT (IntT)
    | ESQPAREN Type DIRPAREN (Type)

Types: Type COMMA Type (Type1::Type2::[])
    | Type COMMA Types (Type::Types)