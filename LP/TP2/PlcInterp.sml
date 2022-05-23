(* PlcInterp *)

exception Impossible
exception HDEmptySeq
exception TLEmptySeq
exception ValueNotFoundInMatch
exception NotAFunc

fun eval (e:expr) (env:plcVal env) : plcVal =
	case e of
		  ConI i => IntV i
		| ConB b => BoolV b
		| Var x => lookup env x
		| ESeq(t) => SeqV([])
		| List([]) => ListV([])
		| List(l) => 
			if (List.length l) > 1 
			then
		 		ListV((List.map (fn (x) => eval x env) l))
			else
				raise Impossible
		| If(e1,v1,v2) => 
			let
				val e2 = eval e1 env
			in
				if (getBoolV(e2)) then (eval v1 env) else (eval v2 env)
			end
		| Let(x, e1, e2) =>
			let
				val v = eval e1 env
				val env2 = (x,v) :: env
			in
				eval e2 env2
			end
		| Letrec(nome, _, l, _, corpo, prog) => eval prog ((nome,Clos(nome,l,corpo,env)) :: env)
		| Anon(_, l, corpo) => Clos("",l, corpo, env)
		| Call(f,params) =>
			let
				val vf = eval f env
			    val paramsEv = eval params env
			in
				case vf of 
					  (Clos("", l, corpo, envP)) => eval corpo ((l, paramsEv) :: envP)
		            | (Clos(f, l, corpo, envP)) => eval corpo ((l, paramsEv) :: (f,vf) :: envP)
			        | _ => raise NotAFunc
			end
		| Match(e2, lOp) => 
			let
				val e3 = eval e2 env
				val opV = List.filter (fn((opcao,retorno)) => 
							case opcao of 
								  SOME(t) => (eval t env) = e3
								| NONE => true
							) lOp
			in
				if(List.null opV) then raise ValueNotFoundInMatch else eval (#2((List.nth (opV, 0)))) env
			end
		| Item(n,e2) =>
			let
				val e3 = eval e2 env
			in
				case e3 of
					ListV(l) => List.nth (l, n-1)
					| _ => raise Impossible
			end
		| Prim1(opr, e1) =>
				let
					val v1 = eval e1 env
				in
					case (opr, v1) of
						  ("!", BoolV v1) => BoolV (not v1)
						| ("-", IntV i) => IntV (~i)
						| ("hd", _) => 
							let in 
								case v1 of
									  SeqV([]) => raise HDEmptySeq
									| SeqV(lista) => hd(lista)
									| _ => raise Impossible
							end
						| ("tl", _) => 
							let in 
								case v1 of
									  SeqV([]) => raise TLEmptySeq
									| SeqV(lista) => SeqV(tl(lista))
									| _ => raise Impossible
							end
						| ("ise", _) => 
							let in
								case v1 of
									  SeqV(lista) => BoolV(List.null lista)
									| _ => raise Impossible
							end
						| ("print", _) =>
							let
								val s = val2string v1
							in
								print(s^"\n"); ListV []
							end
						| _   => raise Impossible
						end
		| Prim2(opr, e1, e2) =>
				let
					val v1 = eval e1 env
					val v2 = eval e2 env
				in
					case (opr, v1, v2) of
						  ("*" , IntV i1, IntV i2) => IntV (i1 * i2)
						| ("/" , IntV i1, IntV i2) => IntV (i1 div i2)
						| ("+" , IntV i1, IntV i2) => IntV (i1 + i2)
						| ("-" , IntV i1, IntV i2) => IntV (i1 - i2)
                        | ("<=", IntV i1, IntV i2) => BoolV (i1 <= i2)
						| ("<" , IntV i1, IntV i2) => BoolV (i1 < i2)
						| ("=" , _, _) => BoolV (v1 = v2)
						| ("!=", _, _) => BoolV (v1 <> v2)
						| ("&&", BoolV b1, BoolV b2) => BoolV (b1 andalso b2)
						| ("::", _, _) => 
							let in 
								case v1 of SeqV(a) => 
									 (case v2 of
										  SeqV(b) => SeqV(a@b)
										| _ => SeqV(v2::a)
									 )
								| _ => (case v2 of 
											  SeqV([]) => SeqV(v1::[]) 
											| SeqV(b) => SeqV(v1::b)
											| _ => raise Impossible
								)	
							end
						| (";" , _ , _) => v2
						| _ => raise Impossible
				end