import pkginfo
import os
import zipfile
import io
import logging
import yaml
import entry_points_txt
from entry_points_txt import EntryPointSet
from hiagent_plugin_sdk.schema import Metadata

class WheelFile:
    def __init__(self, fqn, metadata_version=None):
        self.metadata_version = metadata_version
        self.archive = zipfile.ZipFile(fqn)
        self.names = self.archive.namelist()

    def get_names(self):
        return self.names
    def read(self, name):
        return self.archive.read(name)
    def extract(self, name, target):
        self.archive.extract(name, target)
    def close(self):
        self.archive.close()

class DistFile:
    def __init__(self, fqn, metadata_version=None):
        self.metadata_version = metadata_version
        self.fqn = fqn
        self.names = [os.path.join(fqn, p) for p in os.listdir(fqn)]
    def get_names(self):
        return self.names
    def read(self, name):
        with io.open(name, mode='rb') as inf:
            return inf.read()
    def extract(self, name, target):
        os.system(f"cp {name} {target}")
    def close(self):
        pass

class Wheel(pkginfo.Distribution):

    def __init__(self, filename, metadata_version=None):
        self.filename = filename
        self.metadata_version = metadata_version
        self.extractMetadata()

    def __del__(self):
        if self.reader is not None:
            self.reader.close()

    @property
    def entry_points(self)->EntryPointSet:
        # find and read entry_points.toml first
        tuples = [x.split('/') for x in self.reader.get_names() if 'entry_points' in x]
        schwarz = sorted([(len(x), x) for x in tuples])
        for path in [x[1] for x in schwarz]:
            candidate = '/'.join(path)
            data = self.reader.read(candidate)
            return entry_points_txt.loads(data.decode('utf-8'))
        return {}

    @property
    def metadata(self):
        tuples = [x.split('/') for x in self.reader.get_names() if 'METADATA' in x]
        schwarz = sorted([(len(x), x) for x in tuples])
        for path in [x[1] for x in schwarz]:
            candidate = '/'.join(path)
            data = self.reader.read(candidate)
            if b'Metadata-Version' in data:
                return data
        raise ValueError('No METADATA in archive: %s' % self.filename)

    def extract_dependencies(self, target_dir: str = "/tmp/dist") -> bool:
        has_dependencies = False
        for file in self.reader.get_names():
            logging.debug(f"extract {file}")
            if file.startswith("dependencies/"):
                has_dependencies = True
                self.reader.extract(file, target_dir)
        return has_dependencies

    def extract_metadata(self) -> Metadata | None:
        tuples = [x.split('/') for x in self.reader.get_names() if 'metadata.yaml' in x]
        schwarz = sorted([(len(x), x) for x in tuples])
        for path in [x[1] for x in schwarz]:
            candidate = '/'.join(path)
            data = self.reader.read(candidate)
            data_dict = yaml.safe_load(data.decode('utf-8'))
            return Metadata(**data_dict)
        return None

    def read(self):
        fqn = os.path.abspath(os.path.normpath(self.filename))
        if not os.path.exists(fqn):
            raise ValueError('No such file: %s' % fqn)

        if fqn.endswith('.whl'):
            self.reader = WheelFile(fqn)
        elif fqn.endswith('.dist-info'):
            self.reader = DistFile(fqn)
        else:
            raise ValueError('Not a known wheel archive format or installed .dist-info: %s' % fqn)

        return self.metadata


if __name__ == '__main__':
    file = "/Users/bytedance/Desktop/code.byted.org/plugin-runtime/dist/hiagent_plugin_amap-0.1.4-py3-none-any.whl"
    w = Wheel(file)
    print(w.entry_points)
