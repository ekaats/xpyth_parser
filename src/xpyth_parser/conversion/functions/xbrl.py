def identifier(*args, **kwargs):
    """
    Gets the identifier of one or more XBRL facts
    :param self:
    :return:
    """
    # https://specifications.xbrl.org/registries/functions-registry-1.0/80132%20xfi.identifier/80132%20xfi.identifier%20function.html
    for arg in args[0]:
        context_ref = arg.get("contextRef")
        q = kwargs['query']
        context = q.xpath(f"/xbrli:xbrl/xbrli:context[@id='{context_ref}']/xbrli:entity/xbrli:identifier", namespaces=q.nsmap)
        return context[0].text

function_list = {"xfi:identifier": identifier}
