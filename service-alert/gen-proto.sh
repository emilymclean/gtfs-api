protoc --python_out=alert/ --proto_path ../spec/ gtfs-api.proto
mv alert/gtfs_api_pb2.py alert/format_pb2.py