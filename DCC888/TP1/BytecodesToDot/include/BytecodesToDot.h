#ifndef BYTECODESTODOT_H
#define BYTECODESTODOT_H

#include "llvm/Support/raw_ostream.h"
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/PassManager.h"

namespace llvm {

class BytecodesToDot : public PassInfoMixin<BytecodesToDot> {
public:
   PreservedAnalyses run(Function &F, FunctionAnalysisManager &AM);
};

} // end llvm namespace

#endif // BYTECODESTODOT_H