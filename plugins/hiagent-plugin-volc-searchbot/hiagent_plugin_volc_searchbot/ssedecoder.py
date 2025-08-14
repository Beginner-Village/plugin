from hiagent_plugin_sdk.schema import ServerSentEvent


def decode_sse(line: str) -> ServerSentEvent | None:
    line = line.strip()
    if not line:
        return None
    data = line.removeprefix("data:")
    if data == "[DONE]":
        return ServerSentEvent(event="close", data=data)
    return ServerSentEvent(event="message", data=data)
