render () {
    local outputName="$1"
    local jsonInput="$2"
    local pklInput="$3"
    local extension="$4"
    local encode="$5"
    local proto="$6"

    if [ -z "${pklInput}" ]; then
        outputName="${outputName}" pkl eval "${jsonInput}" -m .
    else
        pkl eval "${jsonInput}" -f json -o "${outputName}${extension}.json"
        pkl eval "${pklInput}" -o "${outputName}${extension}.textpb"
    fi
    protoc "--encode=${encode}" "$proto" < "${outputName}${extension}.textpb" > "${outputName}${extension}.pb"
    sha256sum "${outputName}${extension}.pb" | cut -d " " -f 1 > "${outputName}${extension}.pb.sha"
    sha256sum "${outputName}${extension}.json" | cut -d " " -f 1 > "${outputName}${extension}.json.sha"

    rm "${outputName}${extension}.textpb"
}

renderContent () {
    platform=$1 render "build/canberra/v1/content" "content/content.pkl" "content/protobuf-render.pkl" "$2" "content.Pages" "spec/content.proto"
}

renderContent
renderContent ios ".ios"
renderContent android ".android"

render "build/canberra/v1/journey-config" "config/journey-config.pkl" "" "" "proto.JourneySearchConfigEndpoint" "spec/gtfs-api.proto"