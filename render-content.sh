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

default=true renderContent
language=en renderContent ios ".ios"
language=en renderContent android ".android"
language=zh renderContent ios ".zh.ios"
language=zh renderContent android ".zh.android"
version=0.11.0 language=en renderContent ios "-0.11.0.ios"
version=0.11.0 language=en renderContent android "-0.11.0.android"
version=0.11.0 language=zh renderContent ios "-0.11.0.zh.ios"
version=0.11.0 language=zh renderContent android "-0.11.0.zh.android"

render "build/canberra/v1/journey-config" "config/journey-config.pkl" "" "" "proto.JourneySearchConfigEndpoint" "spec/gtfs-api.proto"