def get_full_headers(default_headers, access_token):
    # construct the authorization header
    auth_header = {
        "authorization": f"Salter {access_token}",
    }

    # full header
    full_header = default_headers | auth_header
    return full_header
