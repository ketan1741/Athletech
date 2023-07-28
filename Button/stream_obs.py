# pip install obs-ws-rc

import asyncio
import keyboard  # You'll need to install the `keyboard` library with `pip install keyboard`
from obswsrc import OBSWS
from obswsrc.requests import StartStreamingRequest, StopStreamingRequest
from obswsrc.types import Stream, StreamSettings, ResponseStatus

async def main():
    async with OBSWS('localhost', 4444, "password") as obsws:
        # Create the StreamSettings object with the desired streaming settings.
        # In this example, it uses the RTMP streaming type with the specified
        # server, stream key, and no authentication.
        stream_settings = StreamSettings(
            server="rtmp://example.org/my_application",
            key="secret_stream_key",
            use_auth=False
        )

        # Create the Stream object with the stream settings and type.
        stream = Stream(
            settings=stream_settings,
            type="rtmp_custom",
        )

        # Send a StartStreamingRequest with the specified stream settings.
        # OBS will start streaming using the provided configuration.
        response = await obsws.require(StartStreamingRequest(stream=stream))

        # Check if the response status indicates success or failure.
        if response.status == ResponseStatus.OK:
            print("Streaming has started")
        else:
            print("Couldn't start the stream! Reason:", response.error)

        # Wait for the "Esc" key press to stop the streaming.
        print("Press 'Esc' key to stop streaming...")
        while True:
            if keyboard.is_pressed('Esc'):
                # Send a StopStreamingRequest to stop the streaming.
                stop_response = await obsws.require(StopStreamingRequest())

                # Check if the response status indicates success or failure.
                if stop_response.status == ResponseStatus.OK:
                    print("Streaming has stopped")
                else:
                    print("Couldn't stop the stream! Reason:", stop_response.error)
                break

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
