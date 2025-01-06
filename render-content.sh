pkl eval content/content.pkl -f json -o content/content.json
pkl eval content/protobuf-render.pkl  -o content/content.Pages.textpb
protoc --encode=content.Pages content/format.proto < content/content.Pages.textpb > content/content.pb
sha256sum content/content.pb | cut -d " " -f 1 > content/content.pb.sha
sha256sum content/content.json | cut -d " " -f 1 > content/content.json.sha