import os
import re
import requests
from tqdm import tqdm
import urllib.parse


class Downloader(requests.Session):
    def download_file(
        self,
        item: dict,
        token: str,
        p: str = "/",
        password: str = None,
        output: str = "./a.out",
        scheme: str = "https",
        netloc: str = "cloud.tsinghua.edu.cn",
        port: int = None,
        chunk_size: int = 8192,
    ):
        response = self.get(
            url=f"{scheme}://{netloc}:{port}/d/{token}/files/"
            if port
            else f"{scheme}://{netloc}/d/{token}/files/",
            params={"p": p, "dl": 1},
            stream=True,
        )
        with tqdm(
            desc=p, total=item["size"], ascii=True, unit="B", unit_scale=True
        ) as progress_bar:
            with open(file=output, mode="wb") as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    file.write(chunk)
                    progress_bar.update(len(chunk))

    def download_dir(
        self,
        token: str,
        p: str = "/",
        password: str = None,
        output: str = "./",
        scheme: str = "https",
        netloc: str = "cloud.tsinghua.edu.cn",
        port: int = None,
    ):
        response = self.get(
            url=f"{scheme}://{netloc}:{port}/api2/d/{token}/dir/"
            if port
            else f"{scheme}://{netloc}/api2/d/{token}/dir/",
            params={"p": p, "password": password},
        )
        json = response.json()
        if isinstance(json, dict):
            raise Exception(str(json))
        os.makedirs(name=output, exist_ok=True)
        for item in json:
            if item["type"] == "dir":
                self.download_dir(
                    token=token,
                    p=os.path.join(p, item["name"]),
                    password=password,
                    output=os.path.join(output, item["name"]),
                    scheme=scheme,
                    netloc=netloc,
                )
            elif item["type"] == "file":
                self.download_file(
                    item=item,
                    token=token,
                    p=os.path.join(p, item["name"]),
                    password=password,
                    output=os.path.join(output, item["name"]),
                    scheme=scheme,
                    netloc=netloc,
                )
            else:
                print(f"Unknown Item: {item}")

    def download_from_link(self, url: str, output: str = "./", password: str = None):
        parse_result: urllib.parse.ParseResult = urllib.parse.urlparse(url=url)

        # parse token
        match_result = re.match(pattern=r"/d/([a-zA-Z0-9]*)/", string=parse_result.path)
        if not match_result:
            raise RuntimeError(f"Invalid URL: {url}")
        token = match_result.group(1)

        # parse file
        query: dict = urllib.parse.parse_qs(qs=parse_result.query)
        p = query["p"][0] if query else "/"
        self.download_dir(
            token=token,
            p=p,
            password=password,
            output=output,
            scheme=parse_result.scheme,
            netloc=parse_result.netloc,
            port=parse_result.port,
        )
