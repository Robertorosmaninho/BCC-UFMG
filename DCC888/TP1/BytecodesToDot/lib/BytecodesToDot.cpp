#ifndef BYTECODESTODOT_CPP
#define BYTECODESTODOT_CPP

#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"

#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

namespace {
struct BytecodesToDot : public FunctionPass {
    static char ID;
    BytecodesToDot() : FunctionPass(ID) {}

    bool runOnFunction(Function &F) override {
        errs() << F.getName() << "\n";
        return false;
    }
}; // end of struct BytecodeToDot
} // end of anonymous namespace

char BytecodesToDot::ID = 0;
static RegisterPass<BytecodesToDot> X("bytecodesToDot",
                                      "Outputs the CFG of the program as a dot file",
                                      false, false);

static RegisterStandardPasses Y(PassManagerBuilder::EP_EarlyAsPossible,
                                []( const PassManagerBuilder &Builder,
                                legacy::PassManagerBase &PM) { PM.add(new BytecodesToDot()); });

#endif // BYTECODESTODOT_CPP