from flask import current_app

def jsonify_model(instance):
    indent = None
    separators = (",", ":")
    
    if current_app.config["JSONIFY_PRETTYPRINT_REGULAR"] or current_app.debug:
        indent = 2
        separators = (", ", ": ")
    
    return current_app.response_class(
        instance.to_json(indent=indent, separators=separators) + "\n",
        mimetype=current_app.config["JSONIFY_MIMETYPE"],
    )