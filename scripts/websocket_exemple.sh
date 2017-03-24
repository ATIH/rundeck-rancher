#!/bin/bash

CONTAINER='1i108662'
BASIC_TOKEN="$(echo "$KEY:$PASS"|base64)"
RANCHER_URL="${RANCHER_URL:=myrancher.nop}"

DATA="$(curl -X POST -H "Authorization: Basic $BASIC_TOKEN" \
-H "Content-Type: application/json" \
-H "Cache-Control: no-cache" \
-d '{
  "attachStdin": false,
  "attachStdout": true,
  "command": [
  "/bin/ls",
  "/"
  ],
"tty": false
}' "https://${RANCHER_URL}/v2-beta/projects/1a10/containers/${CONTAINER}?action=execute")"

token="$(echo "$DATA" | jq --slurp '.[].token' -r)"

wscat --connect wss://${RANCHER_URL}/v2-beta/exec/?token=${token}

exit 0
# ls ->
#connected (press CTRL+C to quit)
#  < LyAjIBtbNm4=
#> bA==
#  < bA==
#> cw==
#  < cw==
#> DQ==
#  < DQo=
#  < G1sxOzM0bWJpbhtbMG0gICAgICAgICAgIBtbMTszNG1saWIbWzBtICAgICAgICAgICAbWzE7MzRtcm9vdBtbMG0gICAgICAgICAgG1sxOzM0bXN5cxtbMG0gICAgICAgICAgIBtbMTszNG12YXIbWzBtDQobWzE7MzRtZGV2G1swbSAgICAgICAgICAgG1sxOzM0bW1lZGlhG1swbSAgICAgICAgIBtbMTszNG1ydW4bWzBtICAgICAgICAgICAbWzE7MzRtdGVzdC1wYXJ0YWdlG1swbQ0KG1sxOzM0bWV0YxtbMG0gICAgICAgICAgIBtbMTszNG1tbnQbWzBtICAgICAgICAgICAbWzE7MzRtc2JpbhtbMG0gICAgICAgICAgG1sxOzM0bXRtcBtbMG0NChtbMTszNG1ob21lG1swbSAgICAgICAgICAbWzE7MzRtcHJvYxtbMG0gICAgICAgICAgG1sxOzM0bXNydhtbMG0gICAgICAgICAgIBtbMTszNG11c3IbWzBtDQovICMgG1s2bg==
#  disconnected
