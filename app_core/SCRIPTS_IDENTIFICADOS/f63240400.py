#!/mnt/sda7/REMI/ARCHIVO_HISTORICO/REMI_local/master_remi_env/bin/python3
import sys
from uvicorn.main import main
if __name__ == '__main__':
    sys.argv[0] = sys.argv[0].removesuffix('.exe')
    sys.exit(main())
