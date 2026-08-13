from wasmtime import Engine, Instance, Module, Store


# the access token sent by the server in the first request is modified in the client.
# the css.wasm file gives five functions each of which returns a index value.
# In the client, these functions are executed and the chasracters at those indexes are dropped in the original access token
def modify_access_token(original_access_token, salt_values):
    # create store which holds the engine.
    engine = Engine()
    store = Store(engine)

    # compile the wasm file
    module = Module.from_file(engine, "css.wasm")

    # Instantiate the model

    instance = Instance(store, module, [])

    # extract the exported functions
    exports = instance.exports(store)

    # call functions
    cdx = exports["cdx"]
    rdx = exports["rdx"]
    bdx = exports["bdx"]
    ndx = exports["ndx"]
    mdx = exports["mdx"]

    # store the indexes
    slice_index_list = []

    # 3rd and 4th parameters are swapped in the last 3 functions
    swapped_salt_values = salt_values[:2]
    swapped_salt_values.extend((salt_values[3], salt_values[2], salt_values[4]))

    slice_index_list.extend(
        (
            cdx(store, *salt_values),
            rdx(store, *salt_values),
            bdx(store, *swapped_salt_values),
            ndx(store, *swapped_salt_values),
            mdx(store, *swapped_salt_values),
        )
    )
    print(slice_index_list)

    # slice the characters at those 5 indexes from original access token.

    # convert string to list
    original_access_token_list = list(original_access_token)

    # delete the characters at those indexes

    # reverse sort the index lists to delete.
    slice_index_list.sort(reverse=True)

    for index in slice_index_list:
        del original_access_token_list[index]

    # join list to get string
    modified_access_token = "".join(original_access_token_list)

    print(modified_access_token)

    return modified_access_token
