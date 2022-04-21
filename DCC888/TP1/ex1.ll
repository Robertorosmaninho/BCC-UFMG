; ModuleID = 'ex1.bc'
source_filename = "ex1.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "arm64-apple-macosx12.0.0"

@.str = private unnamed_addr constant [10 x i8] c"Max = %d\0A\00", align 1

; Function Attrs: noinline nounwind ssp uwtable
define i32 @main(i32 noundef %0, i8** noundef %1) #0 {
  br label %3

3:                                                ; preds = %13, %2
  %.01 = phi i32 [ 1, %2 ], [ %10, %13 ]
  %.0 = phi i32 [ 0, %2 ], [ %.1, %13 ]
  %4 = icmp slt i32 %.01, %0
  br i1 %4, label %5, label %14

5:                                                ; preds = %3
  %6 = sext i32 %.01 to i64
  %7 = getelementptr inbounds i8*, i8** %1, i64 %6
  %8 = load i8*, i8** %7, align 8
  %9 = call i32 @atoi(i8* noundef %8)
  %10 = add nsw i32 %.01, 1
  %11 = icmp sgt i32 %9, %.0
  br i1 %11, label %12, label %13

12:                                               ; preds = %5
  br label %13

13:                                               ; preds = %12, %5
  %.1 = phi i32 [ %9, %12 ], [ %.0, %5 ]
  br label %3, !llvm.loop !10

14:                                               ; preds = %3
  %15 = call i32 (i8*, ...) @printf(i8* noundef getelementptr inbounds ([10 x i8], [10 x i8]* @.str, i64 0, i64 0), i32 noundef %.0)
  ret i32 0
}

declare i32 @atoi(i8* noundef) #1

declare i32 @printf(i8* noundef, ...) #1

attributes #0 = { noinline nounwind ssp uwtable "frame-pointer"="non-leaf" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+v8.5a,+zcm,+zcz" }
attributes #1 = { "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+v8.5a,+zcm,+zcz" }

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5, !6, !7, !8}
!llvm.ident = !{!9}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 12, i32 1]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 1, !"branch-target-enforcement", i32 0}
!3 = !{i32 1, !"sign-return-address", i32 0}
!4 = !{i32 1, !"sign-return-address-all", i32 0}
!5 = !{i32 1, !"sign-return-address-with-bkey", i32 0}
!6 = !{i32 7, !"PIC Level", i32 2}
!7 = !{i32 7, !"uwtable", i32 1}
!8 = !{i32 7, !"frame-pointer", i32 1}
!9 = !{!"clang version 14.0.0 (https://github.com/llvm/llvm-project.git 329fda39c507e8740978d10458451dcdb21563be)"}
!10 = distinct !{!10, !11}
!11 = !{!"llvm.loop.mustprogress"}
