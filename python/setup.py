import os
import shutil
import subprocess
import sys
import stat
from setuptools import setup
from setuptools.command.build_py import build_py

this_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.environ.get("CODESPACE_VSCODE_FOLDER") or os.path.abspath(os.path.join(this_dir, ".."))

# 1. Create PLACEHOLDERS for both folders
# We need both to exist so setuptools recognizes them as packages
for folder in ["xla", "protos"]:
    path = os.path.join(this_dir, folder)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "__init__.py"), "w") as f:
        f.write(f"# Generated {folder.upper()} Namespace\n")

class BazelBuildProtos(build_py):
    def run(self):
        if not os.path.exists(os.path.join(root_dir, "MODULE.bazel")):
             print("Warning: MODULE.bazel not found. Skipping build.")
        else:
            bazel_bin = shutil.which("bazelisk") or shutil.which("bazel")
            subprocess.check_call([bazel_bin, 'build', '//protos:simple_py_proto'], cwd=root_dir)

            gen_root = os.path.join(root_dir, "bazel-bin")
            for root, dirs, files in os.walk(gen_root):
                for f in files:
                    if f.endswith(("_pb2.py", "_pb2.pyi")):
                        source_path = os.path.join(root, f)
                        
                        # 2. Logic to decide WHERE to copy
                        # If the file is your main project proto, put it in 'protos'
                        # If it's the XLA dependency, put it in 'xla'
                        if "simple_proto" in f:
                            target_dir = os.path.join(this_dir, "protos")
                        else:
                            target_dir = os.path.join(this_dir, "xla")
                        
                        dest_path = os.path.join(target_dir, f)
                        
                        # Standard Permission Fix
                        if os.path.exists(dest_path):
                            os.chmod(dest_path, stat.S_IWUSR | stat.S_IRUSR)
                            os.remove(dest_path)

                        shutil.copyfile(source_path, dest_path)
                        os.chmod(dest_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                        print(f"Bundled {f} into {os.path.basename(target_dir)}/")

        super().run()

setup(
    name="my-xla-project-experiment",
    version="0.1.12",
    # 3. Register BOTH sub-packages
    packages=[
        "my_xla_project_experiment", 
        "my_xla_project_experiment.xla", 
        "my_xla_project_experiment.protos"
    ],
    package_dir={
        "my_xla_project_experiment": ".",
        "my_xla_project_experiment.xla": "xla",
        "my_xla_project_experiment.protos": "protos"
    }, 
    package_data={
        "my_xla_project_experiment.xla": ["*.py", "*.pyi"],
        "my_xla_project_experiment.protos": ["*.py", "*.pyi"],
    },
    include_package_data=True,
    cmdclass={'build_py': BazelBuildProtos},
)