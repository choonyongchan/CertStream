import os
import sys
if getattr(sys, 'frozen', False):  # Support correct detection of input files
    os.chdir(os.path.dirname(sys.executable))
elif __file__:
    os.chdir(os.path.dirname(__file__))

import certstream

from src.CertStream import CertStream


def main():
    cs: certstream = CertStream()
    cs.start()


if __name__ == '__main__':
    main()
