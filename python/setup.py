import os
import subprocess
import shutil
from setuptools import setup
from setuptools.command.build_py import build_py

class BazelBuildProtos(build_py):
    def run(self):
        # 1. Reach to the root and build the shared protos
        # The '..' assumes project_a is one level down from root
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        subprocess.check_call(['bazelisk', 'build', '//protos:simple_py_proto'], cwd=root_dir)

        # 2. Copy the generated _pb2.py files into this project's folder
        # This makes them "real files" that pip can package
        gen_dir = os.path.join(root_dir, "bazel-bin", "protos")
        dest_dir = os.path.join(os.path.dirname(__file__), "protos")
        
        if os.path.exists(gen_dir):
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            for f in os.listdir(gen_dir):
                if f.endswith("_pb2.py") or f.endswith("_pb2.pyi"):
                    shutil.copy(os.path.join(gen_dir, f), dest_dir)
        
        super().run()

setup(cmdclass={'build_py': BazelBuildProtos})