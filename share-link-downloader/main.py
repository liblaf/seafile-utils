import argparse
import downloader

parser = argparse.ArgumentParser(
    prog="seafile-share-link-downloader",
    description="Automatically Download files from Seafile share link.",
)
parser.add_argument()
parser.add_argument(
    "--url", action="store", type=str, required=True, help="Seafile share link"
)
parser.add_argument(
    "-o",
    "--output",
    action="store",
    default="./download/",
    type=str,
    required=False,
    help='download location (default: "./download/")',
)
parser.add_argument(
    "-p",
    "--password",
    action="store",
    default=None,
    type=str,
    required=False,
    help="password of Seafile share link (if link is encrypted)",
)


if __name__ == "__main__":
    args = parser.parse_args()
    with downloader.Downloader() as worker:
        worker.download_from_link(
            url=args.url, output=args.output, password=args.password
        )
