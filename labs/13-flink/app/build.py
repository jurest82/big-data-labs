"""Build the package of the application: the connectors and main.py in a zip.

Maven puts the Kinesis and DynamoDB connectors of Flink, with their
dependencies, in one JAR. The zip has that JAR in lib/ and main.py at the top.
"""
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
JAR = HERE / 'target' / 'pyflink-dependencies.jar'
PACKAGE = HERE / 'build' / 'app.zip'


def main():
    subprocess.run(['mvn', '-q', '-B', 'package'], cwd=HERE, check=True)
    PACKAGE.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(PACKAGE, 'w', zipfile.ZIP_DEFLATED) as package:
        package.write(HERE / 'main.py', 'main.py')
        package.write(JAR, 'lib/pyflink-dependencies.jar')
    print(f'{PACKAGE.relative_to(HERE.parent.parent.parent)}: '
          f'{PACKAGE.stat().st_size / 1_000_000:.1f} MB')


if __name__ == '__main__':
    main()
