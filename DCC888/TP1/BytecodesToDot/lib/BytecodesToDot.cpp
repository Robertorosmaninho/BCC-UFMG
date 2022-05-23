#ifndef BYTECODESTODOT_CPP
#define BYTECODESTODOT_CPP

#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"

#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/IR/PassManager.h"

#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

namespace {
struct BytecodesToDot : PassInfoMixin<BytecodesToDot> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
        errs() << F.getName() << "\n";
        return PreservedAnalyses::all();
    }

    static bool isRequired() { return true; }
}; // end of struct BytecodeToDot
} // end of anonymous namespace

llvm::PassPluginLibraryInfo getHelloWorldPluginInfo() {
    return {LLVM_PLUGIN_API_VERSION, "bytecodesToDot", LLVM_VERSION_STRING,
            [](PassBuilder &PB) {
                PB.registerPipelineParsingCallback(
                        [](StringRef Name, FunctionPassManager &FPM,
                           ArrayRef<PassBuilder::PipelineElement>) {
                            if (Name == "bytecodesToDot") {
                                FPM.addPass(BytecodesToDot());
                                return true;
                            }
                            return false;
                        });
            }};
}


extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return getHelloWorldPluginInfo();
}

// "Outputs the CFG of the program as a dot file",

#endif // BYTECODESTODOT_CPP