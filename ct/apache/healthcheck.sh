#!/bin/bash
port=443


#remember to redirect stderr too
if (curl -ks https://localhost:$port 2>&1 | grep -q "Connection refused"); then
        >&2 echo "[FAIL] failed to connect"
        exit 1
fi
