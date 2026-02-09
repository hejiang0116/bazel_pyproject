import os
import shutil
import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

# 1. Absolute Path Logic
# In Codespaces, we use the environment variable as the safest anchor
this_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.environ.get("CODESPACE_VSCODE_FOLDER") or os.path.abspath(os.path.join(this_dir, ".."))

class BazelBuildProtos(build_py):
    def run(self):
        # 2. Only run Bazel if we are actually building, not just metadata gathering
        if not os.path.exists(os.path.join(root_dir, "MODULE.bazel")):
             print(f"Warning: MODULE.bazel not found at {root_dir}. Skipping Bazel build.")
        else:
            bazel_bin = shutil.which("bazelisk") or shutil.which("bazel")
            if not bazel_bin:
                raise RuntimeError("Bazel/Bazelisk not found. Please install it to build protos.")

            print(f"--- Building Protos from Workspace Root: {root_dir} ---")
            subprocess.check_call([bazel_bin, 'build', '//protos:simple_py_proto'], cwd=root_dir)

            # 3. Copy Logic
            gen_dir = os.path.join(root_dir, "bazel-bin", "protos")
            dest_dir = os.path.join(this_dir, "protos")
            os.makedirs(dest_dir, exist_ok=True)
            
            # Ensure __init__.py exists
            with open(os.path.join(dest_dir, "__init__.py"), "a"): pass

            for f in os.listdir(gen_dir):
                if f.endswith(("_pb2.py", "_pb2.pyi")):
                    shutil.copy(os.path.join(gen_dir, f), dest_dir)
                    print(f"Copied generated proto: {f}")

        # 4. Critical: Call the original run()
        super().run()

# 5. The Setup Call
# Keep this as simple as possible so setuptools doesn't get confused
setup(
    name="my-xla-project-experiment",
    version="0.1.0",
    packages=["protos"],
    py_modules=["main"],
    package_dir={"": "."},
    cmdclass={'build_py': BazelBuildProtos},
    # This ensures your metadata is found even during sdist
    author="Your Name",
    description="XLA experiment with Bazel protos",
)