import trafaret as T

SERVER_CONFIG = T.Dict({
    T.Key('local_server'):
        T.Dict({
            'server': T.String(),
            'port': T.Int(),
        }),
    T.Key('debug'): T.Bool(),
})

CLIENT_CONFIG = T.Dict({
    T.Key('blockchain'):
        T.Dict({
            'server': T.String(),
            'service_key': T.String(),
            'service_value': T.String(),
        }),
    T.Key('local_server'):
        T.Dict({
            'server': T.String(),
        }),
    T.Key('debug'): T.Bool(),
})