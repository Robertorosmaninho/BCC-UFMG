
(*
 *  execute "coolc bad.cl" to see the error messages that the coolc parser
 *  generates
 *
 *  execute "myparser bad.cl" to see the error messages that your parser
 *  generates
 *)

(* no error *)
class A {
};

(* error:  b is not a type identifier *)
Class b inherits A {
};

(* error:  a is not a type identifier *)
Class C inherits a {
};

(* error:  keyword inherits is misspelled *)
Class D inherts A {
};

(* error:  closing brace is missing *)
Class E inherits A {
;

(* error: missing ';' *)
class F {
    sum(a:Int, b:Int): Int {
       a + b 
   }
};

(* error: missing 'else' *)
class G inherits F {
    badIfMethod(a : Int): Int {
      if 5 < a then a <- 0 fi 
  };
};

(* error: incorrect use of boolean operators *) 
class H {
  booleanTest(): Bool {
    1 <= 1 <= 2
  };
};

(* error: “>” operator is not defined *)
class I {
  it: Int <- 3;
	loopMethod(): Object { 
      while it > 0 loop it <- it - 1 pool 
  }; 
};

(* error: incorrect let bindings *)
class J {
  letTest () : String {
    let i : Int j : String in y
  };
};

(* error: incorrect use of 'isvoid' *) 
class K {
  isvoidTest () : Bool {
    isvoid isvoid B
  };
};

(* error: loop expression missing delimiter*)
class L {
  it : Int <- 4;
	loopMethod(): Int {
    while 0 < it loop it <- it - 1 
  }; 
};

(* error: missing mother class *)
class M inherits {
  calculator() : Int { 
    sum(5,6) 
   };
};


