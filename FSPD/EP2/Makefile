stubs:
	python3 -m grpc_tools.protoc -I./protos --python_out=./src --grpc_python_out=./src ./protos/service_bank.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./src --grpc_python_out=./src ./protos/service_store.proto

run_serv_banco: stubs
	python3 src/server_bank.py $(arg1) $(arg2)
run_cli_banco: stubs
	python3 src/client_bank.py $(arg1) $(arg2)
run_serv_loja: stubs
	python3 src/server_store.py $(arg1) $(arg2) $(arg3) $(arg4)
run_cli_loja: stubs
	python3 src/client_store.py $(arg1) $(arg2) $(arg3)

clean:
	rm -f src/service_bank_pb2.py src/service_bank_pb2_grpc.py
	rm -f src/service_store_pb2.py src/service_store_pb2_grpc.py
	rm -f -r src/__pycache__