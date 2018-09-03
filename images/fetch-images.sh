#!/usr/bin/env bash

for person in $( awk '{ print $NF }' images-list.txt ); do
	echo "--> $person"
	http --verify=no --download -o="$person.jpg" "https://internal-cdn.amazon.com/badgephotos.amazon.com/?Region=master&FullsizeImage=Yes&uid=$person"
	echo
done

