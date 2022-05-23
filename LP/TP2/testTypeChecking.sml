use "Absyn.sml";

(* Well-typed *)

If(Prim2("=", ConI 11, ConI 12), ConI 1, ConI 0);

Let("b", Prim2("=", ConI 1, ConI 2), If(Var "b", ConI 3, ConI 4));

Letrec("f1",IntT,"x",IntT,Prim2 ("+",Var "x",ConI 1),Call (Var "f1",ConI 12));

(* Ill-typed. Must throw exceptions. *)

Let("b", Prim2("=", ConI 1, ConI 2),If(Var "b", Var "b", ConI 6));

Let("f",Anon (BoolT,"x",If (Var "x",ConI 11,ConI 22)),Call (Var "f",ConI 0));

Letrec("f",BoolT,"x",BoolT,If (Var "x",ConI 11,ConI 22), Call (Var "f",ConB true));
