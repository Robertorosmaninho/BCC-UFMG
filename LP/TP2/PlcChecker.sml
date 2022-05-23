(* PlcChecker *)

exception EmptySeq
exception UnknownType
exception NotEqTypes
exception WrongRetType
exception DiffBrTypes
exception IfCondNotBool
exception NoMatchResults
exception MatchResTypeDiff
exception MatchCondTypesDiff
exception CallTypeMisM
exception NotFunc
exception ListOutOfRange
exception OpNonList

fun checkIsSeqType (t:plcType):bool = 
	case t of 
	  SeqT(_) => true
	| _       => false; 

fun checkEqType (t:plcType):bool = 
	case t of BoolT => true
		| IntT => true
		| ListT([]) => true
		| SeqT (t2) => (checkEqType (t2))
		| ListT(l) => (List.all (checkEqType) l)
		| FunT(_) => false;

fun teval (e:expr) (env: plcType env) : plcType =
	case e of
		  ConI _ => IntT (*2*)
  		| ConB _ => BoolT (*3 e 4*)
		| Var x => lookup env x (*1*)
		| List [] => ListT [] (*5*)
		| List l => 
			let 
				val mapList = map(fn x => teval x env) l 
			in 
				ListT mapList 
			end (*6*)
		| ESeq(SeqT x) => 
			if (checkIsSeqType x) 
			then 
				x
			else raise EmptySeq (*7*)
		| Let(x, e1, e2) =>
				let
					val t = teval e1 env
					val env' = (x,t)::env
				in
					teval e2 env'
				end (*8*)
		| Letrec(nome, t, l, tRet, corpo, prog) => 
			let
				val tcorpo = teval corpo ( (nome, FunT (t, tRet)) :: (l, t) ::env )
				val tprog = teval prog ( (nome, FunT (t,tRet)) :: env )
			in
				if tcorpo = tRet then tprog else raise WrongRetType
			end (*9*)
		| Anon(t, l, e) => 
			let
				val t1 = teval e ((l,t) :: env)
			in
				FunT (t, t1)
			end (*10*)
		| Call(f,params) => 
			let
				val fType = teval f env
				val tparams = teval params env
			in
				case fType of 
					FunT (t,t1) => if tparams = t then t1 else raise CallTypeMisM
					| _ => raise NotFunc
			end (*11*)
		| If(cond, e1, e2) => 
			if (teval cond env) = BoolT
			then
				(let 
					val t1 = teval e1 env
					val t2 = teval e2 env
				in
					if t1 = t2 then t1 else raise DiffBrTypes
				end)
			else raise IfCondNotBool (*12*)
		| Match(expComp, listaOp) => 
			let
				val texprComp = teval expComp env
			in
				if List.null listaOp 
				then
					raise NoMatchResults
				else
					if List.all (fn((opcao,retorno)) => 
									case opcao of 
										  SOME(tipo) => (teval tipo env ) = texprComp
										| NONE => true
								) listaOp
					then
						(let
							val tPrimRetorno = teval (#2 (hd(listaOp))) env
						in
							if List.all (fn((opcao,retorno)) => (teval retorno env) = tPrimRetorno) listaOp
							then 
								tPrimRetorno
							else
								raise MatchResTypeDiff
						end)
					else
						raise MatchCondTypesDiff
			end (*13*)
		| Prim1(opr, e1) =>
				let
					val t1 = teval e1 env
				in
					case (opr, t1) of
						 ("!", _)      => BoolT
						| ("-", _)     => IntT
						| ("hd", _)    => 
							let in
								case t1 of
									SeqT(IntT) => IntT
									| SeqT(BoolT) => BoolT
									| SeqT(ListT []) => raise EmptySeq
									| SeqT(ListT(l)) => ListT(l)
									| SeqT(FunT(a,b)) => FunT(a,b)
									| SeqT(SeqT(a)) => SeqT(a)
									| _ => raise UnknownType
								end
						| ("tl", _)    =>
							let in
								case t1 of 
									SeqT(ListT []) => raise EmptySeq
									| SeqT(_) => t1
									| _ => raise UnknownType
							end
						| ("ise", _)   =>
							let in
								case t1 of 
						SeqT(_) => BoolT
						| _ => raise UnknownType
							end
						| ("print", _) => ListT []
						| _ => raise UnknownType
				end
		| Prim2(opr, e1, e2) =>
				let
					val t1 = teval e1 env
					val t2 = teval e2 env
				in
					if t1 = t2
						then
							case (opr, t1, t2) of
							("*" , IntT, IntT) => IntT
							| ("/" , IntT, IntT) => IntT
							| ("+" , IntT, IntT) => IntT
							| ("-" , IntT, IntT) => IntT
							| ("<=", IntT, IntT) => BoolT
							| ("<" , IntT, IntT) => BoolT
							| ("=", _, _) => if checkEqType t1 then BoolT else raise UnknownType
							| ("!=", _, _) => if checkEqType t1 then BoolT else raise UnknownType
							| ("&&", BoolT, BoolT) => BoolT
							| ("::", _, _) => if t1 = SeqT(t2) then SeqT(t1) else raise UnknownType
							| (";" , _ , _)    => t2
							| _   =>  raise UnknownType
						else
							raise NotEqTypes
				end
		| Item(n, e1) =>
			let
				val t1 = teval e1 env
			in
				case t1 of 
					  ListT([]) => raise ListOutOfRange 
					| ListT(h::t) => 
						if n > ((List.length (h::t))) orelse n < 1
						then 
							raise ListOutOfRange
						else 
							List.nth ((h::t),n-1)
					| _ => raise OpNonList
			end
		| _   =>  raise UnknownType