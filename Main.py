"""This module starts CertStream.
"""
import os
import sys
if getattr(sys, 'frozen', False):  # Support correct detection of input files
    os.chdir(os.path.dirname(sys.executable))
elif __file__:
    os.chdir(os.path.dirname(__file__))

import certstream

from src.CertStream import CertStream


def main() -> None:
    """Main Program of CertStream.
    """
    cs: certstream = CertStream()
    cs.start()


if __name__ == '__main__':
    main()
