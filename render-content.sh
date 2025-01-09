render () {
    platform=$1 pkl eval content/content.pkl -f json -o content/content$2.json
    pkl eval content/protobuf-render.pkl  -o content/content.Pages$2.textpb
    protoc --encode=content.Pages content/format.proto < content/content.Pages$2.textpb > content/content$2.pb
    sha256sum content/content$2.pb | cut -d " " -f 1 > content/content.pb$2.sha
    sha256sum content/content$2.json | cut -d " " -f 1 > content/content.json$2.sha
}

render
render ios ".ios"
render android ".android"