from typing import List
import subprocess
import logging
import zipfile
import os

# empty list means machine arch
TARGET_ARCH: List[str] = [
    # "manylinux2014_x86_64",
    # "manylinux2014_aarch64",
    # "macosx_11_0_arm64",
]


def download_dependencies_multiArch(wheel_path, tmp_dir, target_arch=TARGET_ARCH, index_url="", trust_host=""):
    if not target_arch:
        download_dependencies(wheel_path, "", tmp_dir, index_url, trust_host)
        return
    for arch in target_arch:
        download_dependencies(wheel_path, arch, tmp_dir, index_url, trust_host)

def download_dependencies(wheel_path, platform="", tmp_dir="/tmp", index_url="", trust_host=""):
    cmd = [
        "pip", "download", wheel_path, "-d", f"{tmp_dir}/dependencies",
    ]
    if platform:
        cmd += ["--platform", platform, "--only-binary", ":all:"]
    if index_url:
        cmd += ["--index-url", index_url]
    if trust_host:
        cmd += ["--trusted-host", trust_host]

    ret = subprocess.run(cmd, stderr=subprocess.PIPE)
    err_msg = ret.stderr.decode('utf-8')
    if ret.returncode != 0:
        # output = ret.stdout.decode('utf-8')
        logging.fatal(f"pip download {wheel_path} failed: {err_msg}")

def archive_offline(wheel_path: str, dep_dir, out_path: str, arch):
    offline_filename = os.path.basename(wheel_path).replace(".whl", f".offline.{arch}.whl")
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    archive = zipfile.ZipFile(os.path.join(out_path, offline_filename), "w")
    src = zipfile.ZipFile(wheel_path)
    src.printdir()
    for file in src.filelist:
        if file.filename.startswith("dependencies/"):
            continue
        archive.writestr(file, src.read(file.filename))
    for f in os.listdir(dep_dir):
        filename = os.path.join(dep_dir, f)
        archive.write(filename, os.path.join("dependencies", f))
    archive.printdir()
    archive.close()

def extra_dependencies(wheel_path, dep_dir):
    archive = zipfile.ZipFile(wheel_path)
    for file in archive.filelist:
        print(file.filename)
        if file.filename.startswith("dependencies/"):
            archive.extract(file.filename, dep_dir)
    archive.close()

def install_offline(wheel_path, dep_dir, target_path=""):
    cmd = [
        "pip", "install", wheel_path,
        "--no-index", "--find-link", f"{dep_dir}/dependencies",
    ]
    if target_path != "":
        cmd += ["-t", target_path]

    ret = subprocess.run(cmd, stderr=subprocess.PIPE)
    err_msg = ret.stderr.decode('utf-8')
    if ret.returncode != 0:
        # output = ret.stdout.decode('utf-8')
        logging.fatal(f"pip install offline {wheel_path} failed: {err_msg}")

def package(wheel_path, out_path="", arch="", index_url="", trust_host=""):
    from tempfile import TemporaryDirectory as tmpdir
    with tmpdir() as tmp:
        download_dependencies_multiArch(wheel_path, tmp_dir=tmp, index_url=index_url, trust_host=trust_host)
        archive_offline(wheel_path, os.path.join(tmp, "dependencies"), out_path, arch)

def install(wheel_path, out_path=""):
    from tempfile import TemporaryDirectory as tmpdir
    with tmpdir() as tmp:
        extra_dependencies(wheel_path, dep_dir=tmp)
        install_offline(wheel_path, tmp, out_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="offline patch wheel")
    parser.add_argument("action", help="package | install")
    parser.add_argument("wheel_path", help="wheel path")
    parser.add_argument("--out", help="output path")
    parser.add_argument("--index-url", help="index")
    parser.add_argument("--trust-host", help="trust host")
    parser.add_argument("--arch", help="filename arch suffix")
    # parser.add_argument("--platform", help="target arch", default=",".join(TARGET_ARCH))
    args = parser.parse_args()
    # TARGET_ARCH = args.platform.split(",")

    if args.action == "package":
        package(args.wheel_path, args.out, args.arch, args.index_url, args.trust_host)

    elif args.action == "install":
        install(args.wheel_path, args.out)
    else:
        print("unknown action")
        exit(1)
