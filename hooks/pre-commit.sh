#!/bin/sh
check_encoding() {
	FILE=$1
	REGEX="coding[:=]\s*([-a-zA-Z0-9_.]+)"

	if [[ -s "$1" ]]; then # se o arquivo existe e não é vazio
		head -2 $1 | egrep $REGEX > /dev/null 2> /dev/null;
		if [ $? != "0" ]; then
			echo "ERRO: '$1' não possui definição de encoding" >&2
			exit 1
		fi
	fi
}

export -f check_encoding

check_encoding_recursive() {
    DIR=$1
	find $DIR -name "*.py" -print0 | xargs -0 -i bash -c 'check_encoding "$@"' _ {} \;
}

check_encoding_recursive vestat
