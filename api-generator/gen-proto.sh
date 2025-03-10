protoc --python_out=gen/ --proto_path ../spec/ gtfs-api.proto
mv gen/gtfs_api_pb2.py gen/format_pb2.py
protoc --python_out=gen/ --proto_path ../spec/ network-graph.proto