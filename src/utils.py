def is_datastar(req):
    return req.headers.get("Datastar-Request") == "true"


def render(req, content):
    if is_datastar(req):
        return content
    else:
        return layout(content)