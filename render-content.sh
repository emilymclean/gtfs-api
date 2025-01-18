render () {
    local outputName="$1"
    local jsonInput="$2"
    local pklInput="$3"
    local extension="$4"
    local encode="$5"
    local proto="$6"

    pkl eval "${jsonInput}" -f json -o "${outputName}${extension}.json"
    pkl eval "${pklInput}" -o "${outputName}${extension}.textpb"
    protoc "--encode=${encode}" "$proto" < "${outputName}${extension}.textpb" > "${outputName}${extension}.pb"
    sha256sum "${outputName}${extension}.pb" | cut -d " " -f 1 > "${outputName}${extension}.pb.sha"
    sha256sum "${outputName}${extension}.json" | cut -d " " -f 1 > "${outputName}${extension}.json.sha"

    rm "${outputName}${extension}.textpb"
}

renderContent () {
    platform=$1 render "content/output/content" "content/content.pkl" "content/protobuf-render.pkl" "$2" "content.Pages" "content/format.proto"
}

renderContent
renderContent ios ".ios"
renderContent android ".android"