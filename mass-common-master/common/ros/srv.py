ENVIRONMENT_GET_SRV = "mass/env/get"
EPN_DESTINATION_SRV = "mass/epn/dest"
PATH_SEND_SRV = "mass/control/path_send"

try:
    from mass_common.srv import (
        DestinationSet,
        DestinationSetRequest,
        DestinationSetResponse,
        EnvironmentGet,
        EnvironmentGetRequest,
        EnvironmentGetResponse,
        PathSend,
        PathSendRequest,
        PathSendResponse
    )
except ImportError:
    class DestinationSet:
        pass

    class DestinationSetRequest:
        pass

    class DestinationSetResponse:
        pass

    class EnvironmentGet:
        pass

    class EnvironmentGetRequest:
        pass

    class EnvironmentGetResponse:
        pass

    class PathSend:
        pass

    class PathSendRequest:
        pass

    class PathSendResponse:
        pass
