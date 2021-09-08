/*
 *  cool.y
 *              Parser definition for the COOL language.
 *
 */
%{
#include <iostream>
#include "cool-tree.h"
#include "stringtab.h"
#include "utilities.h"

extern char *curr_filename;

void yyerror(char *s);        /*  defined below; called for each parse error */
extern int yylex();           /*  the entry point to the lexer  */

/************************************************************************/
/*                DONT CHANGE ANYTHING IN THIS SECTION                  */

Program ast_root;	      /* the result of the parse  */
Classes parse_results;        /* for use in semantic analysis */
int omerrs = 0;               /* number of errors in lexing and parsing */
%}

/* A union of all the types that can be the result of parsing actions. */
%union {
  Boolean boolean;
  Symbol symbol;
  Program program;
  Class_ class_;
  Classes classes;
  Feature feature;
  Features features;
  Formal formal;
  Formals formals;
  Case case_;
  Cases cases;
  Expression expression;
  Expressions expressions;
  char *error_msg;
}

/* 
   Declare the terminals; a few have types for associated lexemes.
   The token ERROR is never used in the parser; thus, it is a parse
   error when the lexer returns it.

   The integer following token declaration is the numeric constant used
   to represent that token internally.  Typically, Bison generates these
   on its own, but we give explicit numbers to prevent version parity
   problems (bison 1.25 and earlier start at 258, later versions -- at
   257)
*/
%token CLASS 258 ELSE 259 FI 260 IF 261 IN 262 
%token INHERITS 263 LET 264 LOOP 265 POOL 266 THEN 267 WHILE 268
%token CASE 269 ESAC 270 OF 271 DARROW 272 NEW 273 ISVOID 274
%token <symbol>  STR_CONST 275 INT_CONST 276 
%token <boolean> BOOL_CONST 277
%token <symbol>  TYPEID 278 OBJECTID 279 
%token ASSIGN 280 NOT 281 LE 282 ERROR 283

/*  DON'T CHANGE ANYTHING ABOVE THIS LINE, OR YOUR PARSER WONT WORK       */
/**************************************************************************/
 
   /* Complete the nonterminal list below, giving a type for the semantic
      value of each non terminal. (See section 3.6 in the bison 
      documentation for details). */

/* Declare types for the grammar's non-terminals. */
%type <program> program
%type <classes> class_list
%type <class_> class

%type <formals> formal_list
%type <formal> formal

%type <expression> expression
%type <expression> cond_expression
%type <expression> let_expression
%type <expression> dispatch_expression
%type <expression> while_expression
%type <expressions> expression_block
%type <expressions> expression_list
%type <expression> case_expression

%type <cases> case_branches
%type <case_> case_branch

/* You will want to change the following line. */
%type <features> feature_list
%type <feature> feature

/* Precedence declarations go here. */
%left LET
%right ASSIGN
%left NOT
%nonassoc LE '<' '=' 
%left '+' '-' 
%left '*' '/'
%left ISVOID
%left '~'
%left '@'
%left '.'
%left '(' ')'

%%
program : class_list { 
  @$ = @1; 
  ast_root = program($1); 
};
    
class_list : class { 
  $$ = single_Classes($1); /* single class */
  parse_results = $$; 
}
| class_list class { 
  $$ = append_Classes($1,single_Classes($2)); /* multiple class */
  parse_results = $$; 
};

class	: CLASS TYPEID '{' '}' ';' {
  $$ = class_($2, idtable.add_string("Object"), nil_Features(), 
              stringtable.add_string(curr_filename));
}
| CLASS TYPEID '{' feature_list '}' ';' { 
  $$ = class_($2, idtable.add_string("Object"), $4, 
              stringtable.add_string(curr_filename)); 
}
| CLASS TYPEID INHERITS TYPEID '{' '}' ';' { 
  $$ = class_($2, $4, nil_Features(), stringtable.add_string(curr_filename));
}
| CLASS TYPEID INHERITS TYPEID '{' feature_list '}' ';' { 
  $$ = class_($2, $4, $6, stringtable.add_string(curr_filename)); 
} 
| CLASS ERROR ';' class {
  $$ = $4;
};

/* Feature list may be empty, but no empty features in list. */
feature_list : feature {
  $$ = single_Features($1);
}
| feature_list feature {
  $$ = append_Features($1, single_Features($2));
};

feature : OBJECTID '(' formal_list ')' ':' TYPEID '{' expression '}' ';' {
  $$ = method($1, $3, $6, $8);
}
| OBJECTID '(' ')' ':' TYPEID '{' expression '}' ';' {
  $$ = method($1, nil_Formals(), $5, $7);
}
| OBJECTID ':' TYPEID ASSIGN expression ';' {
  $$ = attr($1, $3, $5);
}
| OBJECTID ':' TYPEID ';' {
  $$ = attr($1, $3, no_expr());
};


formal_list : formal {
  $$ = single_Formals($1);
}
| formal_list ',' formal {
  $$ = append_Formals($1, single_Formals($3));
};

formal : OBJECTID ':' TYPEID {
  $$ = formal($1, $3);
};

expression : INT_CONST {
  $$ = int_const($1);
}
| BOOL_CONST {
  $$ = bool_const($1);
}
| STR_CONST {
  $$ = string_const($1);
}
| OBJECTID {
  $$ = object($1);
}
| '(' expression ')' { 
  $$ = $2; 
}
| '{' expression_block '}' { 
    $$ = block($2); 
}
| OBJECTID ASSIGN expression {
  $$ = assign($1, $3);
}
| expression LE expression {
  $$ = leq($1, $3);
}
| expression '<' expression {
  $$ = lt($1, $3);
}
| expression '=' expression {
  $$ = eq($1, $3);
}
| '~' expression {
  $$ = neg($2);
}
| expression '*' expression {
  $$ = mul($1, $3);
}
| expression '/' expression {
  $$ = divide($1, $3);
}
| expression '+' expression {
  $$ = plus($1, $3);
}
| expression '-' expression {
  $$ = sub($1, $3);
}
| NEW TYPEID {
  $$ = new_($2);
}
| ISVOID expression {
  $$ = isvoid($2);
}
| NOT expression {
  $$ = comp($2);
}

| cond_expression
| dispatch_expression
| while_expression
| case_expression
| let_expression
| ERROR expression {
  $$ = $2;
};
;
expression_list : expression {
  $$ = single_Expressions($1);
}
| expression_list ',' expression {
  $$ = append_Expressions($1, single_Expressions($3));
};

expression_block : expression ';'{ // TODO: Verificar se n seria expression ;
  $$ = single_Expressions($1);
}
| expression_block expression ';' {
    $$ = append_Expressions($1, single_Expressions($2));
}
| expression_block ';' ERROR ';' ;

case_expression : CASE expression OF case_branches ESAC {
  $$ = typcase($2, $4);
};

case_branches : case_branch ';' {
  $$ = single_Cases($1);
}
| case_branches case_branch ';' {
  $$ = append_Cases($1, single_Cases($2));
};

case_branch : OBJECTID ':' TYPEID DARROW expression {
  $$ = branch($1, $3, $5);
};

while_expression : WHILE expression LOOP expression POOL {
  $$ = loop($2, $4);
};

dispatch_expression : expression '.' OBJECTID '(' expression_list ')' {
  $$ = dispatch($1, $3, $5);
}
| OBJECTID '(' ')' {
  Entry *self = idtable.add_string("self");
  $$ = dispatch(object(self), $1, nil_Expressions());
}
| OBJECTID '(' expression_list ')' {
  Entry *self = idtable.add_string("self");
  $$ = dispatch(object(self), $1, $3);
}
| expression '.' OBJECTID '(' ')' {
  $$ = dispatch($1, $3, nil_Expressions());
}

| expression '@' TYPEID '.' OBJECTID '(' ')' {
  $$ = static_dispatch($1, $3, $5, nil_Expressions());
}
| expression '@' TYPEID '.' OBJECTID '(' expression_list ')' {
  $$ = static_dispatch($1, $3, $5, $7);
};

cond_expression : IF expression THEN expression FI { // TODO: Isso aqui é mesmo necessário?
  $$ = cond($2, $4, no_expr());
}
| IF expression THEN expression ELSE expression FI {
  $$ = cond($2, $4, $6);
};

let_expression 
  : LET OBJECTID ':' TYPEID ASSIGN expression IN expression %prec ASSIGN {
  $$ = let($2, $4, $6, $8);
}
| LET OBJECTID ':' TYPEID IN expression %prec ASSIGN {
  $$ = let($2, $4, no_expr(), $6);
}
| LET OBJECTID ':' TYPEID ',' let_expression {
  $$ = let($2, $4, no_expr(), $6);
}
| LET OBJECTID ':' TYPEID ASSIGN expression ',' let_expression {
  $$ = let($2, $4, $6, $8);
}
| OBJECTID ':' TYPEID ASSIGN expression IN expression %prec ASSIGN {
  $$ = let($1, $3, $5, $7);
}
| OBJECTID ':' TYPEID IN expression %prec ASSIGN {
  $$ = let($1, $3, no_expr(), $5);
}
| OBJECTID ':' TYPEID ',' let_expression {
  $$ = let($1, $3, no_expr(), $5);
}
| OBJECTID ':' TYPEID ASSIGN expression ',' let_expression {
  $$ = let($1, $3, $5, $7);
}
| LET ERROR ',' let_expression {
  $$ = $4;
};

/* end of grammar */
%%

/* This function is called automatically when Bison detects a parse error. */
void yyerror(char *s)
{
  extern int curr_lineno;

  cerr << "\"" << curr_filename << "\", line " << curr_lineno << ": " \
    << s << " at or near ";
  print_cool_token(yychar);
  cerr << endl;
  omerrs++;

  if(omerrs>50) {fprintf(stdout, "More than 50 errors\n"); exit(1);}
}

