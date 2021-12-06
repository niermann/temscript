#!/usr/bin/python
from temscript.server import MicroscopeServer


def run_server(argv=None, microscope_factory=None):
    """
    Main program for running the server

    :param argv: Arguments
    :type argv: List of str (see sys.argv)
    :param microscope_factory: Factory function for creation of microscope
    :type microscope_factory: callable without arguments
    :returns: Exit code
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080, help="Specify port on which the server is listening")
    parser.add_argument("--host", type=str, default='', help="Specify host address on which the the server is listening")
    args = parser.parse_args(argv)

    try:
        # Create a web server and define the handler to manage the incoming request
        server = MicroscopeServer((args.host, args.port), microscope_factory=microscope_factory)
        print("Started httpserver on host '%s' port %d." % (args.host, args.port))
        print("Press Ctrl+C to stop server.")

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('Ctrl+C received, shutting down the web server')
        server.socket.close()

    return 0


if __name__ == '__main__':
    from temscript import NullMicroscope
    run_server(microscope_factory=NullMicroscope)
