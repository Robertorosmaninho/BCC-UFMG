class A {
};

Class BB__ inherits A {
};

Class C {

  loopTest(value: Int): Int {
    while (value < 0) loop
      value <- value - 1
    pool
  };

  ifElseTest(value: Bool): Bool {
    if value 
      then true 
    else if false 
      then true 
    else false 
      fi 
    fi
  };
  
  caseTest(object: Object): String {
    case (object) of
      s: String => "String";
      o: Object => "Object"; 
    esac
  };

  letTest(): String { let a: Int, b: Int, c: Int in a+b+c };

  opBlockTest(input: Int): Int { {
      1 + 1;
      2 - 2;
      10 / 2;
      5 * 2;
      input <- 0;
      10 < 5;
      11 <= 5;
      11 = 11;
    }
  };
};

class D inherits IO {
    sayHi(): Object { out_string("Hi D\n") };
};

class E inherits D {
    sayHi(): Object { out_string("Hi E\n") };
};

class F inherits E {
    sayHi(): Object { out_string("Hi F\n") };
};

class Main inherits IO {
    f: F <- new F;
    staticDispatchTest(): Object { { {
                f@D.sayHi();
            }; }
    };
};
